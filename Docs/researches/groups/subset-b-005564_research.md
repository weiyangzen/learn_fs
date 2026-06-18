# Group Research: subset-b-005564

This grouped report covers the requested fbdev source subset. Each file section is delimited so the reconciliation lane can split it into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.c

## Purpose
Implements Matrox G450/G550 on-chip secondary output support for the matroxfb driver. It registers a TV-capable secondary output and a DVI output, computes PAL/NTSC CVE2 encoder register images, programs those registers through the DAC index/data ports, and exposes V4L2-style controls for TV brightness, contrast, saturation, hue, and test output.

## Important APIs, Types, and Functions
- `struct mctl` maps a `v4l2_queryctrl` descriptor to a field offset inside `struct matrox_fb_info`.
- `g450_controls[]` defines supported TV controls and defaults stored in `minfo->altout.tvo_params`.
- `cve2_get_reg()`, `cve2_set_reg()`, and `cve2_set_reg10()` access CVE2 encoder registers through `matroxfb_DAC_out()` and `matroxfb_DAC_in()` while holding the Matrox DAC IRQ lock.
- `computeRegs()` derives CVE2 timing, chroma subcarrier, sync, blanking, and modified `struct my_timming` values for TV output.
- `cve2_init_TVdata()` seeds PAL or NTSC register templates and output timing descriptors.
- `matroxfb_g450_compute()`, `matroxfb_g450_program()`, and `matroxfb_g450_verify_mode()` implement `struct matrox_altout` callbacks for the secondary TV/monitor output.
- `g450_dvi_compute()` implements the DVI output clock programming path.
- `matroxfb_g450_connect()` and `matroxfb_g450_shutdown()` are exported entry points used by the base matroxfb device code.

## Control Flow
On connect, if `minfo->devflags.g450dac` is set, the driver takes `minfo->altout.lock`, fills TV control defaults, and installs two output descriptors: output 1 as `matroxfb_g450_altout` and output 2 as `matroxfb_g450_dvi`. The compute callback distinguishes CRTC2 TV modes from monitor modes. For TV modes, it copies the PAL/NTSC template, patches brightness/contrast/saturation/hue/test bits, then calls `computeRegs()` to adjust clock and timing. For monitor modes or DVI, it programs the G450 pixel/video PLL if `mt->mnp` is unset. The program callback writes the prepared CVE2 register image for TV modes.

## State and Persistence
Persistent runtime state lives in `struct matrox_fb_info`: `outputs[]` entries, `altout.tvo_params`, and the prepared `minfo->hw.maven` register image. The module has no independent persistent storage. Control writes immediately update both stored parameters and hardware registers, so state changes are visible without a full mode reprogram for supported controls.

## Dependencies and Integration Points
The file depends on matroxfb core types and locking from `matroxfb_base.h`, DAC helpers from `matroxfb_misc.c`, G450 PLL helpers from `g450_pll.h`, and public output/control constants from `<linux/matroxfb.h>`. It integrates through the `matrox_altout` callback table and exported connect/shutdown functions.

## Risks
The TV register programming is hardware-specific and mostly magic constants; invalid timing math can generate unusable output. `computeRegs()` mutates the caller's `struct my_timming`, so ordering with CRTC programming matters. DAC register access relies on correct lock discipline. The control lookup assumes ordered control IDs. Some arithmetic is constrained by CVE2 line length assumptions and can silently clamp visible width.

## Test Signals
Useful validation signals include successful module load with `g450dac`, output 1 and 2 registration, PAL/NTSC/monitor mode acceptance through `verifymode`, visible TV output after CRTC2 programming, DVI clock stability, and live control changes reflected in CVE2 registers 0x0e/0x1e, 0x20/0x22, 0x25, and 0x05. Regression tests should exercise invalid controls and unsupported output modes returning `-EINVAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.h

## Purpose
Declares the public G450/G550 output hooks used by the matroxfb base driver. It provides real prototypes when `CONFIG_FB_MATROX_G` is enabled and no-op inline stubs otherwise.

## Important APIs, Types, and Functions
- `matroxfb_g450_connect(struct matrox_fb_info *minfo)` installs G450 secondary/DVI output handlers.
- `matroxfb_g450_shutdown(struct matrox_fb_info *minfo)` removes those handlers.

## Control Flow
Including code calls these functions unconditionally. The header hides configuration differences by compiling to no-ops when the G450 support object is not built.

## State and Persistence
The header holds no state. The real implementation mutates `struct matrox_fb_info` output state.

## Dependencies and Integration Points
Includes `matroxfb_base.h` for `struct matrox_fb_info`. It is consumed by Matrox core initialization and shutdown paths.

## Risks
The no-op stubs make missing `CONFIG_FB_MATROX_G` support silent. Call sites must not assume output registration happened unless device flags and build config allow it.

## Test Signals
Build coverage with and without `CONFIG_FB_MATROX_G` should confirm call sites compile. Runtime validation is whether G450 outputs appear only in the enabled configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_g450.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.c

## Purpose
Implements the Matrox Maven/MGA-TVO external TV encoder driver as an I2C client. It attaches the encoder to the primary matroxfb head, exposes the secondary output through `struct matrox_altout`, computes monitor and TV timing register images, pushes long encoder register sequences over I2C/SMBus, and provides V4L2-style TV controls including brightness, contrast, saturation, hue, gamma, test output, and deflicker.

## Important APIs, Types, and Functions
- `struct maven_data` links an I2C client to the primary `matrox_fb_info` and stores detected MGA-TVO revision.
- `maven_controls[]` and `maven_gamma[]` define user-visible controls and hardware gamma presets.
- `maven_get_reg()`, `maven_set_reg()`, and `maven_set_reg_pair()` implement byte and word register I/O over the I2C adapter.
- `matroxfb_PLL_mavenclock()`, `matroxfb_mavenclock()`, and `DAC1064_calcclock()` compute encoder and monitor PLL parameters.
- `maven_init_TVdata()`, `maven_compute_timming()`, and `maven_program_timming()` prepare and program register images for PAL, NTSC, and monitor modes.
- `maven_set_control()` updates stored control state and writes corresponding live encoder registers.
- `maven_altout` is the alt-output operation table installed in `minfo->outputs[1]`.
- `maven_probe()` and `maven_remove()` are the I2C driver entry points registered by `module_i2c_driver()`.

## Control Flow
During probe, the driver checks adapter functionality for SMBus word/byte and protocol-mangling support, allocates `maven_data`, then calls `maven_init_client()`. Initialization derives the owning `matrox_fb_info` from the `i2c_bit_adapter`, installs the secondary output under `altout.lock`, reads register 0xB2 to classify the encoder as MGATVO_B or MGATVO_C, and fills TV control defaults. Mode setting enters through the alt-output compute callback: monitor modes get DAC1064-style clock and display timing registers; TV modes start from PAL/NTSC templates, find exact line clocks, compute horizontal/vertical resampling parameters, and set output mode to composite/S-Video. Programming either writes the monitor timing register list or calls `maven_init_TV()` for the full TV sequence. Start triggers a resync by writing register 0x95.

## State and Persistence
State is split between `maven_data`, `minfo->outputs[1]`, `minfo->altout.tvo_params`, and the shared `minfo->hw.maven` register image. The I2C client data owns the Maven attachment lifecycle. Control values persist only in memory and are reapplied during timing computation; live control changes also update hardware immediately.

## Dependencies and Integration Points
Depends on `matroxfb_maven.h`, shared PLL/VGA helpers from `matroxfb_misc.h`, DAC constants from `matroxfb_DAC1064.h`, Linux I2C APIs, and `<linux/matroxfb.h>` output/control definitions. It integrates with Matrox software I2C adapters via `struct i2c_bit_adapter` and with the fb output routing layer through `struct matrox_altout`.

## Risks
The register programming sequence is long, timing-sensitive, and largely hardware-magic. I2C read helpers log failures but still return the uninitialized local destination masked to 8 bits if `i2c_transfer()` fails, which can obscure hardware communication errors. Arithmetic in clock and resampling selection can reject modes or produce marginal values. Control offsets assume `struct matrox_fb_info` layout. Removal must clear `outputs[1]` under the lock to avoid stale output callbacks.

## Test Signals
Validation should include I2C probe on an adapter with required functionality, successful secondary output registration, correct MGATVO_B/C detection, mode verification for PAL/NTSC/monitor, visible monitor pass-through and TV output, and live control writes to brightness/contrast/gamma/deflicker registers. Negative signals include `-EINVAL` for unsupported modes, failed clock matching, and I2C write/read error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.h

## Purpose
Defines the Matrox software I2C adapter wrapper used by Maven and related Matrox output code.

## Important APIs, Types, and Functions
- `struct i2c_bit_adapter` embeds an `i2c_adapter`, initialization flag, `i2c_algo_bit_data`, owning `matrox_fb_info *`, and bit masks for data/clock GPIO lines.

## Control Flow
The header is not executable, but `matroxfb_maven.c` uses `container_of(clnt->adapter, struct i2c_bit_adapter, adapter)` to recover the Matrox framebuffer instance for an I2C client.

## State and Persistence
The adapter tracks whether it has been initialized, the owning Matrox card, and the bit masks used by the bit-banged bus. Lifetime is controlled by the Matrox base/I2C setup code outside this file.

## Dependencies and Integration Points
Includes Linux ioctl and I2C headers, `i2c-algo-bit`, and `matroxfb_base.h`. It is an integration contract between Matrox framebuffer state and Linux I2C client drivers such as Maven.

## Risks
Because clients recover `matrox_fb_info` through this exact embedding, layout and adapter ownership must remain consistent. Misconfigured masks or initialization state will break downstream I2C devices.

## Test Signals
Build tests should cover I2C-enabled Matrox configurations. Runtime signals are I2C adapter registration, successful Maven client probe, and correct recovery of `minfo` from the adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_maven.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.c

## Purpose
Provides shared Matrox framebuffer support routines: DAC indexed I/O, conversion from fbdev var timing to Matrox internal timing, generic PLL search, VGA register image construction/restoration, BIOS and PInS parsing, and default board limit setup. These functions are exported for other Matrox modules.

## Important APIs, Types, and Functions
- `matroxfb_DAC_out()` and `matroxfb_DAC_in()` write/read RAMDAC registers using Matrox MMIO helpers.
- `matroxfb_var2my()` converts `fb_var_screeninfo` into `struct my_timming`.
- `matroxfb_PLL_calcclock()` searches input/feed/post divisors for requested frequency within `struct matrox_pll_features` limits.
- `matroxfb_vgaHWinit()` fills `minfo->hw` VGA sequencer, graphics, attribute, CRTC, and CRTCEXT register images from internal timing.
- `matroxfb_vgaHWrestore()` writes saved VGA state and DAC palette back to hardware in a critical section.
- `parse_bios()`, `get_pins()`, and version/output helpers decode Matrox BIOS and PInS metadata.
- `parse_pins1()` through `parse_pins5()` and matching defaults populate clock, memory, and register limits for generations from Millennium through G550.
- `matroxfb_read_pins()` maps the PCI ROM or x86 legacy BIOS area, parses metadata, restores PCI ROM state, and applies parsed/default limits.

## Control Flow
Mode preparation first converts fbdev timing with `matroxfb_var2my()`, computes PLL values, then calls `matroxfb_vgaHWinit()` to derive VGA-compatible register fields. Restore writes the resulting image to sequencer, CRTC, graphics, attribute, palette, and misc registers. Device initialization calls `matroxfb_read_pins()`, temporarily enables and maps the ROM, parses BIOS/PInS, optionally falls back to the legacy x86 VGA BIOS window, and then calls `matroxfb_set_limits()`. Limit setup always seeds chip-family defaults first, then overrides them only when BIOS/PInS data is valid and has a recognized version and length.

## State and Persistence
The file mutates `struct matrox_fb_info` fields including `hw`, `bios`, `limits`, `values`, `features.pll`, `max_pixel_clock_panellink`, and memory flags. It also temporarily modifies PCI ROM and option registers, then restores them. No state survives outside driver memory and hardware registers.

## Dependencies and Integration Points
Relies on `matroxfb_base.h` abstractions through `matroxfb_misc.h`, Linux PCI and IO helpers, interrupt/critical-section macros, and unaligned little-endian readers. Exports are consumed by DAC, G450/Maven, and base Matrox mode-setting paths.

## Risks
BIOS parsing trusts many fixed offsets after basic length/version checks; malformed PInS content can produce bad memory timing. `matroxfb_vgaHWinit()` mutates `struct my_timming` for double-scan and interlace, so callers must avoid reusing the original without understanding those changes. Hardware restore touches legacy VGA state and palette broadly. PCI ROM remapping must be restored on every path.

## Test Signals
Signals include correct PInS version detection, sane printed PInS memory type, stable mode programming across bpp/interlace/double-scan cases, unchanged PCI ROM config after probing, and successful module symbol resolution for dependent Matrox components. Negative tests should cover invalid BIOS signatures, invalid PInS checksums/lengths, and unsupported PInS versions falling back to defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.h

## Purpose
Declares shared Matrox helper APIs for PLL calculation, VGA hardware initialization/restoration, and BIOS/PInS reading.

## Important APIs, Types, and Functions
- `matroxfb_PLL_calcclock()` is the exported generic PLL divider search.
- `PLL_calcclock()` is a convenience inline using `minfo->features.pll`.
- `matroxfb_vgaHWinit()` and `matroxfb_vgaHWrestore()` create and apply VGA register state.
- `matroxfb_read_pins()` extracts BIOS power-up information and applies hardware limits.

## Control Flow
The header enables other Matrox modules to call common routines without duplicating PLL or VGA register logic. The inline simply forwards to the exported function with per-device PLL features.

## State and Persistence
No header-local state. Called functions mutate `struct matrox_fb_info` and hardware registers.

## Dependencies and Integration Points
Includes `matroxfb_base.h` for core Matrox structures and is included by DAC, Maven, G450, and base driver code.

## Risks
All declarations expose low-level hardware mutation; call sites must already hold the appropriate higher-level mode-setting discipline. The inline depends on `features.pll` having been initialized, usually by `matroxfb_read_pins()`.

## Test Signals
Compile all Matrox submodules against this header and verify mode setup calls resolve. Runtime test signal is successful PLL calculation after BIOS/PInS initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/maxinefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/maxinefb.c

## Purpose
Implements the DECstation 5000/xx "Maxine" onboard framebuffer driver. It registers a fixed 1024x768 8bpp pseudocolor framebuffer, controls the Inmos IMS332 RAMDAC palette and cursor RAM, and exposes default fbdev sysmem/IOMEM operations.

## Important APIs, Types, and Functions
- `maxinefb_defined` and `maxinefb_fix` describe the fixed mode and memory layout.
- `maxinefb_ims332_write_register()` and `maxinefb_ims332_read_register()` access IMS332 registers through architecture-specific physical addresses.
- `maxinefb_setcolreg()` converts 16-bit fbdev color components to 8-bit DAC values and writes palette registers.
- `maxinefb_init()` validates machine type, clears framebuffer memory, erases cursor RAM, initializes `fb_info`, allocates a 256-entry cmap, and registers the framebuffer.
- `maxinefb_exit()` unregisters the framebuffer.

## Control Flow
Module init first honors `fb_get_options("maxinefb")`; disabled options return `-ENODEV`. It then requires `mips_machtype == MACH_DS5000_XX`. On matching hardware, it clears part of the framebuffer, sets the fixed physical start, clears 512 cursor RAM entries, populates the static `fb_info`, allocates a color map, and calls `register_framebuffer()`.

## State and Persistence
Uses one static `struct fb_info` and static mode structures. Hardware palette and cursor RAM persist in device registers until changed. The driver does not dynamically allocate private state beyond the cmap.

## Dependencies and Integration Points
Depends on MIPS boot machine type constants and `video/maxinefb.h` address/register definitions. Integrates with fbdev through `fb_ops`, `FB_DEFAULT_IOMEM_OPS`, color map allocation, and module init/exit.

## Risks
The driver performs direct volatile physical memory accesses without `ioremap`, matching old platform conventions but risky outside the exact platform. It clears only `0x1ffff` bytes despite a 1024x768 framebuffer length. `maxinefb_ims332_read_register()` is non-static while not declared here, so external users may rely on it. Failure after `fb_alloc_cmap()` but before registration is not fully cleaned up.

## Test Signals
Validation requires booting on `MACH_DS5000_XX`, seeing registration of a 1024x768x8 framebuffer, palette changes through fbdev colormap operations, and hidden hardware cursor after init. Non-Maxine machines should return `-EINVAL`; disabled options should return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/maxinefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/Makefile

## Purpose
Builds the Fujitsu MB862xx framebuffer driver object from its main driver and acceleration support, with optional I2C adapter support.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_FB_MB862XX) += mb862xxfb.o` creates the composite driver object.
- `mb862xxfb-y := mb862xxfbdrv.o mb862xxfb_accel.o` always includes main fbdev and acceleration code.
- `mb862xxfb-$(CONFIG_FB_MB862XX_I2C) += mb862xx-i2c.o` conditionally adds the hardware I2C adapter.

## Control Flow
Kbuild links the listed objects into `mb862xxfb.o` only when the driver config is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates MB862xx source files into the kernel build and reflects the optional I2C integration declared in `mb862xxfb.h`.

## Risks
If `CONFIG_FB_MB862XX_I2C` is disabled, `mb862xx_i2c_init()` compiles to an inline no-op, so boards needing DDC or I2C devices will silently lack that bus.

## Test Signals
Build matrix should cover `CONFIG_FB_MB862XX` on/off and `CONFIG_FB_MB862XX_I2C` on/off, verifying the expected object members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx-i2c.c

## Purpose
Implements an I2C master adapter for MB862xx GDC hardware, used by Coral-P(A)/Lime style framebuffer devices when `CONFIG_FB_MB862XX_I2C` is enabled.

## Important APIs, Types, and Functions
- `mb862xx_i2c_wait_event()` polls bus control/status for interrupt or bus error completion.
- `mb862xx_i2c_do_address()` emits address phases and manages repeated-start state in `par->i2c_rs`.
- `mb862xx_i2c_read_byte()` and `mb862xx_i2c_write_byte()` transfer one data byte through GDC I2C registers.
- `mb862xx_xfer()` implements `i2c_algorithm.master_xfer`.
- `mb862xx_i2c_init()` attaches a static `i2c_adapter` to the framebuffer private data and registers it.
- `mb862xx_i2c_exit()` unregisters the adapter.

## Control Flow
I2C core calls `mb862xx_xfer()` with message arrays. For each non-empty message, the driver writes the address, then calls the read or write loop. After at least one message it emits STOP and disables the bus. Reads request ACK for all but the final byte. Writes return `-EIO` on NACK or bus error.

## State and Persistence
The adapter uses `struct mb862xxfb_par` as `algo_data`, primarily for register base access and `i2c_rs` repeated-start tracking. `par->adap` records whether the adapter is registered.

## Dependencies and Integration Points
Uses MB862xx register macros from `mb862xx_reg.h`, `inreg/outreg` from `mb862xxfb.h`, Linux I2C core, and udelay polling. Called by the PCI/CoralP initialization and removal paths.

## Risks
`mb862xx_i2c_wait_event()` has no timeout and can spin forever if hardware never sets completion or bus error. The adapter object is static, so multiple device instances would share one adapter and `algo_data`. `functionality()` advertises only `I2C_FUNC_SMBUS_BYTE_DATA` even though the transfer path is raw master_xfer-like.

## Test Signals
Validation includes successful adapter registration, transfers returning the number of completed messages, STOP after multi-message operations, repeated-start behavior for combined transactions, and error propagation on bus error/NACK. Hardware lockup tests should expose the missing timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx_reg.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx_reg.h

## Purpose
Defines MB862xx/MB86297 framebuffer, display, capture, I2C, host, DRAM controller, and interrupt register offsets and bit constants.

## Important APIs, Types, and Functions
- Base offsets such as `MB862XX_MMIO_BASE`, `MB862XX_DISP_BASE`, and Carmine-specific register windows.
- Display controller registers such as `GC_DCM1`, `GC_L0M`, `GC_HDB_HDP`, `GC_VTR`, palette, cursor, layer, and capture registers.
- I2C register and bit definitions such as `GC_I2C_BCR`, `I2C_START`, `I2C_REPEATED_START`, `I2C_BER`, and `I2C_LRB`.
- Carmine DRAM initialization constants and clock/interrupt constants.

## Control Flow
No executable control flow. The main driver, I2C adapter, and acceleration code use these constants to address hardware registers through `inreg()` and `outreg()`.

## State and Persistence
No state in the header. The defined registers represent persistent device hardware state when written by driver code.

## Dependencies and Integration Points
Included by all MB862xx implementation files. It is the shared hardware contract for platform/PCI setup, display programming, capture layer controls, I2C transfers, and interrupt handling.

## Risks
Incorrect offsets or masks can corrupt unrelated hardware blocks. Some constants are board-specific evaluation-board values, especially Carmine DRAM timings. The header combines multiple chip generations, so call sites must select offsets based on `par->type` and mapped base windows correctly.

## Test Signals
Build tests ensure all MB862xx sources agree on names. Runtime signals include correct chip identification, successful display timing programming, working I2C, stable capture layer setup, and interrupt acknowledge behavior on both CoralP/Lime and Carmine paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xx_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb.h

## Purpose
Defines MB862xx framebuffer user ioctls, device IDs, core enums, board mode data, private framebuffer state, helper declarations, and register access macros.

## Important APIs, Types, and Functions
- `struct mb862xx_l1_cfg` describes layer-1 capture/overlay source, destination, scale, and mirror parameters.
- `MB862XX_L1_GET_CFG`, `MB862XX_L1_SET_CFG`, `MB862XX_L1_ENABLE`, and `MB862XX_L1_CAP_CTL` are fbdev ioctl commands.
- `enum gdctype` identifies supported controller families.
- `struct mb862xx_gc_mode` carries default mode, default bpp, VRAM size, clock, and memory mode settings.
- `struct mb862xxfb_par` stores fbdev pointer, device/PCI handles, mapped framebuffer/MMIO windows, per-block register bases, IRQ, type, clock, I2C adapter, capture state, layer config, and pseudo palette.
- `inreg()` and `outreg()` abstract raw vs normal MMIO access depending on Lime configuration.

## Control Flow
The header does not execute, but it shapes all MB862xx driver flow. The main driver allocates `struct mb862xxfb_par` as `fb_info->par`, initializes base pointers, and uses access macros throughout.

## State and Persistence
`struct mb862xxfb_par` is the central persistent runtime state for each framebuffer instance. It stores mapped resources, hardware subtype, capture buffer offsets, current layer-1 config, and color palette.

## Dependencies and Integration Points
Integrates user ABI ioctls with `mb862xxfbdrv.c`, optional I2C hooks with `mb862xx-i2c.c`, acceleration initialization with `mb862xxfb_accel.c`, and PCI/platform hardware IDs with kernel bus matching.

## Risks
The ioctl definitions pass pointer-typed structure arguments in `_IOR/_IOW`, which is unusual ABI shape. The header has a compile-time conflict guard for mutually exclusive Lime and PCI GDC configs. Register access macros rely on a local variable named `par`, constraining call-site style.

## Test Signals
Compile both Lime and PCI configurations separately, including I2C on/off. Runtime validation includes successful ioctl copy paths, correct mapped register base setup for each `gdctype`, and no accidental simultaneous Lime/PCI config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.c

## Purpose
Provides 2D acceleration hooks for MB862xx framebuffer operations: rectangle fill, copyarea, and imageblit through the GDC geometry FIFO.

## Important APIs, Types, and Functions
- `mb862xxfb_write_fifo()` writes command words to the geometry FIFO, polling free count from `GDC_REG_FIFO_COUNT`.
- `mb86290fb_copyarea()` emits BLT copy commands, selecting direction based on source/destination overlap.
- `mb86290fb_imageblit1()`, `mb86290fb_imageblit8()`, and `mb86290fb_imageblit16()` build FIFO command arrays for 1bpp, 8bpp, and 16bpp images.
- `mb86290fb_imageblit()` clips image blits to virtual resolution, allocates DMA-capable command memory, and falls back to cfb on unsupported depths or allocation failure.
- `mb86290fb_fillrect()` clips fills, chooses XOR or COPY ROP, and emits draw-rect commands.
- `mb862xxfb_init_accel()` installs accelerated fbops for non-32bpp modes and cfb helpers for 32bpp.

## Control Flow
The main driver calls `mb862xxfb_init_accel()` during `set_par()` for CoralP devices. The function sets display/engine registers and replaces fbops. Subsequent fbdev drawing operations build command arrays and feed them to the hardware FIFO. Unsupported image depths and allocation failures fall back to generic cfb implementations.

## State and Persistence
The file updates `fb_ops` function pointers, `info->flags`, `info->fix.accel`, and GDC draw/display registers. `mb862xxfb_write_fifo()` uses a static `free` counter shared by all calls and instances.

## Dependencies and Integration Points
Depends on `mb862xxfb.h`, `mb862xx_reg.h`, and `mb862xxfb_accel.h` command/register constants. Integrates with fbdev drawing callbacks and the main driver's mode setup path.

## Risks
The static FIFO free counter is global rather than per device, problematic for multiple adapters or after hardware reset. `mb86290fb_imageblit16()` copies `step` bytes rather than `step << 2` bytes, which is suspicious because command buffers are u32 words. 8bpp blitting reads pixel pairs and may overread odd widths after clipping. No explicit engine idle synchronization is done before changing mode or unloading.

## Test Signals
Use fbcon and framebuffer drawing tests across 8, 16, and 32bpp. Verify 32bpp uses cfb helpers, non-32bpp sets hardware acceleration flags, copyarea handles overlapping directions, imageblit clips at virtual bounds, and FIFO polling does not hang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.h

## Purpose
Defines MB862xx GDC 2D/3D geometry engine register offsets, command codes, type codes, color register selectors, and raster operation constants used by acceleration code.

## Important APIs, Types, and Functions
- FIFO and engine registers such as `GDC_GEO_REG_INPUT_FIFO`, `GDC_REG_FIFO_COUNT`, `GDC_REG_MODE_BITMAP`, `GDC_REG_DRAW_BASE`, and `GDC_REG_X_RESOLUTION`.
- Drawing command codes such as `GDC_CMD_BLT_FILL`, `GDC_CMD_BLT_DRAW`, `GDC_CMD_BITMAP`, and directional BLT copy codes.
- Packet type codes such as `GDC_TYPE_SETREGISTER`, `GDC_TYPE_SETCOLORREGISTER`, `GDC_TYPE_DRAWRECTP`, `GDC_TYPE_DRAWBITMAPP`, and `GDC_TYPE_BLTCOPYP`.
- Raster operations `GDC_ROP_COPY`, `GDC_ROP_XOR`, and related ROP constants.

## Control Flow
No executable flow. `mb862xxfb_accel.c` composes command words by shifting these type and command constants into FIFO packet positions.

## State and Persistence
No software state. Constants refer to hardware engine state changed by emitted commands.

## Dependencies and Integration Points
Included by the acceleration implementation and indirectly tied to the GDC hardware command FIFO.

## Risks
The header is a large set of magic numeric constants with limited type safety. A typo in command composition can issue an unintended engine command. Several constants mention reserved or MB86293-later behavior, so callers must avoid using unsupported commands on older chips.

## Test Signals
Compile acceleration code and validate emitted command sequences on hardware or emulator traces. Visual tests for fill, copy, and imageblit are the practical regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfb_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfbdrv.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfbdrv.c

## Purpose
Implements the main Fujitsu MB862xx framebuffer driver for platform/OpenFirmware Lime-style devices and PCI CoralP/Carmine GDCs. It manages resource mapping, chip initialization, fbdev setup, display timing programming, palette operations, panning, blanking, layer-1 capture/overlay ioctls, interrupts, and device removal.

## Important APIs, Types, and Functions
- Timing helpers `h_total()`, `v_total()`, `hsp()`, `vsp()`, and `d_pitch()` compute register values from fbdev var state.
- `mb862xxfb_setcolreg()`, `mb862xxfb_check_var()`, `mb862xxfb_set_par()`, `mb862xxfb_pan()`, `mb862xxfb_blank()`, and `mb862xxfb_ioctl()` implement fbdev operations.
- `mb862xxfb_init_fbinfo()` initializes fixed/variable fbdev state, detects bootloader display configuration, reserves capture buffers, and initializes capture registers.
- `dispregs_show()` exposes selected display/draw/geo register dumps through sysfs.
- `mb862xx_intr()` acknowledges interrupts differently for Carmine and non-Carmine devices.
- `mb862xx_gdc_init()` initializes Lime host-bus devices.
- `coralp_init()`, `init_dram_ctrl()`, and `carmine_init()` initialize PCI variants.
- `of_platform_mb862xx_probe/remove()` and `mb862xx_pci_probe/remove()` handle bus-specific lifecycles.
- `mb862xxfb_init()` and `mb862xxfb_exit()` register the enabled platform and/or PCI drivers.

## Control Flow
Probe allocates `fb_info` with `mb862xxfb_par`, maps framebuffer and MMIO resources, initializes chip-specific register base pointers and clocks, requests IRQ, initializes fb state, allocates color map, programs initial mode, registers the framebuffer, creates the `dispregs` sysfs file, and enables interrupts. `set_par()` optionally installs acceleration for CoralP, disables display, sets clock divider, layer format/dimensions/timings, disables cursors, then re-enables display. Ioctls manipulate layer-1 capture scaling, mirroring, enable state, and capture state. Remove disables display/interrupts, removes sysfs, unregisters fbdev, unmaps resources, releases IRQ/regions, and frees the framebuffer object.

## State and Persistence
`struct mb862xxfb_par` owns all runtime state: resource mapping, chip type, register windows, IRQ, mode defaults, I2C adapter, capture buffer offsets, layer config, and pseudo palette. Hardware state includes display controller timings, palette registers, capture registers, interrupt masks, DRAM controller programming, and clock/reset registers. `pre_init` preserves bootloader display setup when detected or configured.

## Dependencies and Integration Points
Depends on Linux fbdev, PCI, platform/OF, aperture removal, IRQ, MMIO, and optional I2C support. Integrates with `mb862xx_reg.h`, `mb862xxfb.h`, optional acceleration, optional Lime/PCI configs, and user space through fbdev ioctls and sysfs.

## Risks
`mb862xxfb_check_var()` uses `d_pitch(&fbi->var)` while modifying `var`, so validation may use stale state instead of the candidate mode. `mb862xxfb_ioctl()` treats `arg` directly as `int *` for enable commands instead of copying from user, which is unsafe for fb ioctl ABI. `mb862xx_pci_probe()` does not call `mb862xx_i2c_exit()` on all CoralP failure paths after `coralp_init()`. Capture buffer reservation assumes enough mapped VRAM. Some probe errors return the initial `-ENODEV` in platform paths rather than the exact failure.

## Test Signals
Test platform and PCI probe/remove, bootloader-preinitialized and driver-initialized modes, 8/16/32bpp check/set_par paths, palette writes, panning registers, blank/unblank, sysfs register dump, IRQ ack for Carmine and CoralP/Lime, layer-1 ioctl get/set/enable/capture, acceleration on CoralP, and cleanup after mid-probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mb862xx/mb862xxfbdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/metronomefb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/metronomefb.c

## Purpose
Implements an fbdev driver for E-Ink Metronome display controllers. It exposes a virtual 8bpp grayscale framebuffer, loads and decodes a waveform firmware file into board-provided contiguous memory, initializes the controller through board callbacks, and updates the display using deferred IO or damage callbacks.

## Important APIs, Types, and Functions
- `struct epd_frame` and `epd_frame_table[]` describe supported panel frame sizes, controller config words, and expected waveform sizes.
- `struct waveform_hdr` models the firmware waveform header.
- `load_waveform()` validates firmware size/version/checksums and run-length decodes waveform data into `par->metromem_wfm`.
- `metronome_powerup_cmd()`, `metronome_config_cmd()`, `metronome_init_cmd()`, and `metronome_display_cmd()` prepare command blocks and wait through board callbacks.
- `metronomefb_dpy_update()` copies the full framebuffer to controller image memory and appends checksum.
- `metronomefb_dpy_deferred_io()` updates dirty pages, maintains per-page checksum cache, and triggers display.
- `metronomefb_probe()` allocates fb state, requests firmware, sets up board memory/IRQ/IO, initializes fbdefio and cmap, and registers the framebuffer.
- `metronomefb_remove()` unregisters and releases resources.

## Control Flow
Probe requires platform data containing a `struct metronome_board`. It pins the board module, allocates `fb_info`, chooses the frame table entry from board panel type, allocates virtual framebuffer memory plus a spare page, allocates a checksum table, asks the board driver to set up physical controller memory, requests `metronome.wbf`, decodes it for mode 3 and temperature 31, sets up IRQ and controller registers, initializes deferred IO, sets an 8-level grayscale colormap, and registers fbdev. Writes are captured by deferred IO; dirty pages are swizzled into Metronome image memory and a display command is issued.

## State and Persistence
Persistent state lives in `struct metronomefb_par`: board callbacks, controller memory pointers, waveform/image/command areas, DMA address, waitqueue, frame count, checksum table, and panel type. The virtual framebuffer is vmalloc memory in `info->screen_buffer`; controller-facing memory is allocated by the board driver. Module parameter `user_wfm_size` can override expected waveform size.

## Dependencies and Integration Points
Depends on `video/metronomefb.h` board interface, platform devices, firmware loading, fbdev deferred IO, vmalloc, DMA address reporting, and board-specific implementations such as AM200-class drivers. Firmware `metronome.wbf` is declared with `MODULE_FIRMWARE`.

## Risks
`load_waveform()` performs complex offset parsing; while many bounds checks exist, the RLE decode increments `mem_idx` without explicit bounds against allocated waveform memory. `csum_table` is allocated as `videomemorysize/PAGE_SIZE` bytes but stores `u16` checksums, which appears undersized. Damage-range/area callbacks force full updates, while deferred IO page path uses swizzled 3-bit data, so update paths differ. Probe cleanup uses `board->cleanup()` for both IRQ and framebuffer cleanup after setup, relying on board implementation discipline.

## Test Signals
Test probe with each supported panel type, missing platform data, missing firmware, bad firmware size/version/checksum, full framebuffer updates, deferred dirty-page updates, board wait callbacks timing out, colormap content, and remove cleanup. Visible display update and correct command checksum/opcode alternation are key runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/metronomefb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Kconfig

## Purpose
Defines the top-level Kconfig entry for the Marvell MMP display subsystem and includes submenus for hardware controller, panel, and framebuffer components.

## Important APIs, Types, and Functions
- `menuconfig MMP_DISP` is a tristate option depending on `CPU_PXA910 || CPU_MMP2 || COMPILE_TEST`.
- Includes `mmp/hw/Kconfig`, `mmp/panel/Kconfig`, and `mmp/fb/Kconfig` only when `MMP_DISP` is enabled.

## Control Flow
Kconfig exposes the subsystem root option and conditionally exposes subordinate options inside the `if MMP_DISP` block.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls build visibility for MMP display controller, panel, and fbdev drivers.

## Risks
Because component configs are nested under `MMP_DISP`, enabling a framebuffer or panel alone is impossible without the framework root. `COMPILE_TEST` broadens build coverage to non-target architectures but does not make hardware runnable.

## Test Signals
Run Kconfig/build combinations for target CPUs and `COMPILE_TEST`, verifying all nested configs appear only under `MMP_DISP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Makefile

## Purpose
Builds the Marvell MMP display framework root object and descends into hardware, panel, and framebuffer subdirectories when `CONFIG_MMP_DISP` is enabled.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_DISP) += mmp_disp.o hw/ panel/ fb/`.
- `mmp_disp-y += core.o` links the registry framework implementation.

## Control Flow
Kbuild compiles `core.o` into `mmp_disp.o` and builds child directories under the same config gate.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects `core.c` and the MMP subdirectories to the kernel build.

## Risks
All child directories are visited under the root config, but their own object inclusion still depends on nested configs. Misconfigured dependencies can compile panel/fb code without usable platform devices.

## Test Signals
Build with `CONFIG_MMP_DISP=m/y` and verify `mmp_disp.o` plus configured children are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/core.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/core.c

## Purpose
Implements the Marvell MMP display subsystem core registry. It tracks display paths and panels, matches them by platform path name, initializes path overlays, and exports lookup/register/unregister APIs used by hardware controller, panel, and framebuffer drivers.

## Important APIs, Types, and Functions
- `panel_list`, `path_list`, and `disp_lock` are the global registry state.
- `path_get_overlay()`, `path_check_status()`, and `path_get_modelist()` are default path operations.
- `mmp_register_panel()` and `mmp_unregister_panel()` manage panel list membership and path binding.
- `mmp_get_path()` finds a registered path by name for framebuffer drivers.
- `mmp_register_path()` allocates a flexible `struct mmp_path`, copies platform information, matches an existing panel, initializes overlay objects, and adds it to `path_list`.
- `mmp_unregister_path()` removes and frees a path.

## Control Flow
Hardware controller drivers register paths with `mmp_register_path()`. Panel drivers independently register panels with `mmp_register_panel()`. Both registration flows search the opposite list by name to connect `path->panel`. Framebuffer drivers later call `mmp_get_path()` and `mmp_path_get_overlay()` to access the registered hardware path and overlay.

## State and Persistence
Path and panel registration state persists in global lists protected by `disp_lock`. Each path owns overlay objects and per-path/overlay mutexes until unregister. No persistent storage exists beyond memory.

## Dependencies and Integration Points
Uses public display types from `<video/mmp_disp.h>`, Linux lists, mutexes, module exports, and dynamic allocation. Exports are consumed by `mmp_ctrl.c`, `mmpfb.c`, and panel drivers such as `tpo_tj032md01bw.c`.

## Risks
Name matching with `strcmp()` is the only binding mechanism; platform data mismatch leaves components disconnected. `mmp_get_path()` returns a pointer after releasing `disp_lock`, so callers rely on platform lifetime ordering to avoid unregister races. `mmp_unregister_path()` does not disconnect a panel pointer explicitly before freeing. `mmp_register_path()` returns NULL on allocation failure but some callers treat zero as generic failure.

## Test Signals
Test panel-before-path and path-before-panel registration orders, path lookup by name, overlay count and ID initialization, unregister cleanup, and behavior when names do not match. Module symbol consumers should load in arbitrary order without crashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Kconfig

## Purpose
Defines the fbdev frontend option for the Marvell MMP display subsystem.

## Important APIs, Types, and Functions
- `config MMP_FB` is a tristate option depending on `FB`.
- It selects `FB_IOMEM_HELPERS` and defaults to `y`.

## Control Flow
Kconfig exposes the MMP framebuffer driver when the enclosing MMP display menu is active and fbdev core is available.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Builds the framebuffer driver that consumes MMP paths and overlays from the core/hardware layer.

## Risks
Defaulting to `y` can build the fb frontend even when no platform data creates a usable path; probe still fails gracefully if platform data is missing.

## Test Signals
Kconfig/build validation with `FB` enabled/disabled and `MMP_DISP` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Makefile

## Purpose
Builds the MMP framebuffer frontend object.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_FB) += mmpfb.o`.

## Control Flow
Kbuild compiles `mmpfb.c` when `CONFIG_MMP_FB` is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the fbdev frontend to the kernel build under the MMP display subsystem.

## Risks
None beyond config dependency correctness.

## Test Signals
Build with `CONFIG_MMP_FB=m/y` and ensure `mmpfb.o` is emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.c

## Purpose
Implements the fbdev frontend for Marvell MMP display paths. It converts fbdev pixel formats and modes into MMP display modes/windows, allocates coherent framebuffer memory, wires fb operations to overlay/path APIs, and registers `/dev/fb*` devices.

## Important APIs, Types, and Functions
- `var_to_pixfmt()` and `pixfmt_to_var()` translate between fbdev bitfields and MMP `PIXFMT_*` values.
- `fbmode_to_mmpmode()` and `mmpmode_to_fbmode()` translate between fbdev video modes and MMP display modes.
- `mmpfb_check_var()`, `mmpfb_set_par()`, `mmpfb_setcolreg()`, `mmpfb_pan_display()`, and `mmpfb_blank()` implement fbdev operations.
- `var_update()` selects a matching or best video mode, normalizes pixel format, doubles virtual Y, and updates fixed info.
- `mmpfb_set_win()` programs overlay window geometry and pitches.
- `modes_setup()` imports modes from the selected path/panel.
- `mmpfb_probe()` consumes platform data, gets path/overlay, allocates DMA coherent framebuffer memory, powers on the overlay, initializes fb_info, and registers the framebuffer.

## Control Flow
Probe requires `struct mmp_buffer_driver_mach_info` platform data. It allocates `fb_info`, initializes default format, gets a registered path by name, gets an overlay by ID, assigns the DMA fetch ID, imports panel modes if present, sizes the framebuffer, allocates coherent memory, powers the overlay if modes exist, sets up fb_info/cmap, and registers fbdev. `set_par()` normalizes the requested var, programs the path mode, overlay window, and overlay address. Panning recomputes the base physical address from offsets and updates the overlay address. Blanking toggles overlay/path power through `mmpfb_power()`.

## State and Persistence
`struct mmpfb_info` stores platform identity, current fb mode, pixel format, DMA framebuffer address and size, selected path/overlay, pseudo palette, and output format. The coherent framebuffer memory persists until driver teardown, but this source has no remove function, so release is not implemented.

## Dependencies and Integration Points
Depends on the MMP core and hardware path API from `<video/mmp_disp.h>`, Linux fbdev, platform data, and DMA coherent allocation. It relies on `mmp_ctrl.c` or another hardware provider registering paths before probe.

## Risks
The driver rejects 8bpp in `mmpfb_check_var()` even though format conversion and visual logic know about pseudocolor. It has no platform driver remove callback, so framebuffer memory and registration are not cleaned up on device removal. `mmpfb_setcolreg()` does not program pseudocolor hardware palette. `modes_setup()` returns 0 when no modelist exists, causing a large default allocation but no path mode power-on. `info->screen_buffer` is used for coherent memory rather than the more common `screen_base` field.

## Test Signals
Test path lookup failure, overlay lookup failure, panel modelist import, fb registration, mode changes across RGB/YUV formats, panning address calculation, blank/unblank overlay state, coherent framebuffer allocation size, and module/device removal behavior. Visual tests should confirm overlay pitch and pixel format programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.h

## Purpose
Defines the private state for the Marvell MMP fbdev frontend and its default framebuffer allocation size.

## Important APIs, Types, and Functions
- `struct mmpfb_info` stores device pointer, fb_info, current output mode, pixel format, framebuffer CPU/DMA addresses, selected overlay/path, access mutex, pseudo palette, and output format.
- `MMPFB_DEFAULT_SIZE` reserves enough memory for two 1920x1080 32bpp buffers.

## Control Flow
The header is consumed by `mmpfb.c`; `struct mmpfb_info` is allocated as the private area of `fb_info`.

## State and Persistence
All frontend runtime state for an MMP framebuffer instance persists in `struct mmpfb_info` while the platform device is bound.

## Dependencies and Integration Points
Includes `<video/mmp_disp.h>` for path/overlay/mode types and `<linux/fb.h>` for fbdev structures.

## Risks
The `access_ok` mutex is initialized in probe but not heavily used in the current frontend, so it may give a false sense of synchronization. `fb_size` is an `int`, which is adequate for the default size but less robust for larger buffers.

## Test Signals
Compile the framebuffer frontend and verify private data allocation, DMA address assignment, and pseudo palette writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/fb/mmpfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Kconfig

## Purpose
Defines MMP display hardware controller and optional LCD-controller SPI-port configuration.

## Important APIs, Types, and Functions
- `config MMP_DISP_CONTROLLER` is a bool depending on clocks, I/O memory, and MMP/PXA910/compile-test platform support.
- `config MMP_DISP_SPI` is a bool depending on `MMP_DISP_CONTROLLER && SPI_MASTER` and defaults to `y`.

## Control Flow
Kconfig exposes the hardware controller option and, when available, the SPI master option used for panel initialization.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls compilation of `mmp_ctrl.o` and `mmp_spi.o` from the hw Makefile.

## Risks
Default SPI support depends on `SPI_MASTER`; missing it prevents SPI panels from initializing through the LCD controller.

## Test Signals
Build matrix should cover controller only, controller plus SPI, and compile-test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Makefile

## Purpose
Builds MMP display hardware controller and optional SPI master objects.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_DISP_CONTROLLER) += mmp_ctrl.o`.
- `obj-$(CONFIG_MMP_DISP_SPI) += mmp_spi.o`.

## Control Flow
Kbuild includes hardware support objects according to Kconfig selections.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects MMP hardware implementation sources to the kernel build.

## Risks
If `mmp_spi.o` is omitted, panel drivers expecting the LCD SPI bus will not probe unless another SPI controller provides the bus/device.

## Test Signals
Build with both Kconfig options and verify object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.c

## Purpose
Implements the Marvell MMP LCD/display controller hardware provider. It maps controller registers, enables clocks, handles interrupts, registers MMP display paths with overlay operations, programs timing/pixel clock/interface registers, and optionally registers the LCD-controller SPI bus.

## Important APIs, Types, and Functions
- `ctrl_handle_irq()` masks and clears pending LCD interrupt status.
- `fmt_to_reg()` translates MMP pixel formats into DMA control register bits including RGB/YUV swap and CSC enable.
- `overlay_set_win()`, `overlay_set_addr()`, `overlay_set_onoff()`, and `overlay_set_fetch()` implement hardware overlay operations.
- `path_onoff()`, `path_enabledisable()`, and `path_set_mode()` manage path power, panel callbacks, display timings, interface polarity, and pixel clock divisor.
- `ctrl_set_default()` initializes global LCD control and interrupt enable/mask defaults.
- `path_set_default()`, `path_init()`, and `path_deinit()` configure path defaults and register/unregister paths with the MMP core.
- `mmphw_probe()` is the platform driver probe for `mmp-disp`.

## Control Flow
Probe gets memory and IRQ resources plus `mmp_mach_plat_info`, allocates `mmphw_ctrl` with one `mmphw_path_plat` per configured path, requests/maps registers, requests IRQ, enables the named clock, initializes global registers, registers each path into the core, then registers the LCD SPI master when enabled. Framebuffer clients later call overlay/path ops: `set_par()` in `mmpfb.c` leads to `path_set_mode()`, `overlay_set_win()`, `overlay_set_addr()`, and `overlay_set_onoff()`.

## State and Persistence
`struct mmphw_ctrl` stores platform name, IRQ, MMIO base, clock, device, mutex, and flexible path-platform array. Each path platform stores config/link/rbswap bits and the registered `mmp_path`. Hardware state includes LCD global control, DMA control, path timing registers, SCLK divisors, interface mode/rbswap registers, and overlay DMA addresses.

## Dependencies and Integration Points
Depends on `mmp_ctrl.h`, `<video/mmp_disp.h>`, platform data, devm resource APIs, clocks, IRQ handling, and optional `lcd_spi_register()` from `mmp_spi.c`. Exposes hardware to `core.c` through `mmp_register_path()`.

## Risks
There is no remove callback, so registered paths and optional SPI host are not explicitly unregistered on device removal. `ctrl_handle_irq()` writes `~isr` to clear status, which depends on write-one/zero semantics being exactly as expected. Pixel clock divider is integer-only and does not handle zero or out-of-range divisors robustly. `path_init()` returns 0 for allocation or registration failure, losing detailed error codes.

## Test Signals
Test platform probe with valid/invalid resources and platform data, IRQ clear under status bits, path registration count and names, panel power callbacks on overlay enable/disable, pixel format conversion for RGB/YUV formats, timing register programming, clock divisor values, and SPI bus registration when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.h

## Purpose
Defines the Marvell MMP LCD controller register layout, bitfield macros, path helpers, DSI/LVDS register structures, and private hardware controller/path state used by `mmp_ctrl.c` and `mmp_spi.c`.

## Important APIs, Types, and Functions
- `struct lcd_regs` maps path-local video, graphics, cursor, timing, blanking, color key, and vsync registers.
- Macros such as `dma_ctrl()`, `intf_ctrl()`, `LCD_SCLK()`, `dma_fmt()`, `dma_mask()`, and interrupt mask helpers compose register offsets and bitfields for different paths.
- Register definitions cover graphics/video DMA, smart/dumb panel SPI, interrupts, SRAM, DSI, LVDS, I/O pad modes, alpha, dither, and timing-master controls.
- `enum { PATH_PN, PATH_TV, PATH_P2 }` identifies controller paths.
- `struct mmphw_path_plat` links an MMP core path to hardware-specific config.
- `struct mmphw_ctrl` stores controller-wide MMIO, clock, IRQ, and path-platform state.
- Inline helpers `overlay_is_vid()`, `path_to_ctrl()`, `ctrl_regs()`, and `path_regs()` translate public path/overlay objects into hardware register views.
- `lcd_spi_register()` is declared when SPI support is enabled.

## Control Flow
The header itself is declarative. Runtime code uses `path_regs()` to select the correct register block for PN, TV, or P2 paths and uses bit macros to update format, DMA, interrupts, clock, and interface settings.

## State and Persistence
No independent state, but it defines the state containers allocated by the controller driver and the layout of persistent hardware registers.

## Dependencies and Integration Points
Includes `<video/mmp_disp.h>` for public MMP display objects. It is the private integration contract between MMP hardware controller, SPI adapter, and any code touching LCD controller registers.

## Risks
This header is broad and hardware-specific; incorrect path IDs can trigger `BUG_ON(1)` in `path_regs()`. Numerous bitfield macros assume register semantics and path mappings. Some comments identify guessed or duplicated definitions, especially PN2 interrupt masks and DSI macro duplication. Because state structs are private, external code must go through the public MMP display API.

## Test Signals
Compile all MMP hardware and SPI configurations. Runtime validation includes correct register block selection for PN/TV/P2 paths, expected DMA format bits for each `PIXFMT_*`, interrupt mask composition, SPI register access, and DSI/LVDS builds even when not actively used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_spi.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_spi.c

## Purpose
Registers and implements an SPI master backed by the MMP LCD controller's smart-panel/SPI port so panel drivers can send initialization commands through the display controller.

## Important APIs, Types, and Functions
- `lcd_spi_write()` writes one 8/16/32-bit word to `LCD_SPU_SPI_TXDATA`, starts transfer via `LCD_SPU_SPI_CTRL`, polls SPI interrupt status, and clears the start bit/status.
- `lcd_spi_setup()` configures bit count, clock count, chip select, SPI enable, 3-wire/4-wire mode, and I/O pad mode.
- `lcd_spi_one_transfer()` iterates spi_message transfers and writes each word according to `spi->bits_per_word`.
- `lcd_spi_register()` allocates a `spi_controller`, stores the LCD register base in controller private data, sets bus number 5, and registers the controller.

## Control Flow
`mmp_ctrl.c` calls `lcd_spi_register()` after controller/path initialization. SPI core calls setup for devices, then transfer for messages. Each transfer word is synchronously written and polled until the SPI IRQ bit appears or a timeout expires; completion callback is invoked at the end of the message.

## State and Persistence
The SPI controller stores only a pointer to the LCD controller MMIO base in its private data. Hardware SPI control and I/O pad registers persist in the LCD controller. No unregister path is provided in this source.

## Dependencies and Integration Points
Depends on `mmp_ctrl.h`, Linux SPI core, I/O accessors, and the controller driver's `mmphw_ctrl`. Consumed by panel drivers such as `tpo_tj032md01bw.c`.

## Risks
The transfer implementation ignores `lcd_spi_write()` return values, always sets `m->status = 0`, and calls completion even after timeouts. It uses legacy `ctlr->transfer` rather than newer queued transfer hooks. The fixed bus number 5 can conflict in unusual systems. No cleanup/unregister path appears in the controller remove flow.

## Test Signals
Validate SPI controller registration, panel `spi_setup()` with 16-bit words, visible writes to `LCD_SPU_SPI_CTRL/TXDATA`, timeout logging when IRQ never arrives, and correct failure propagation once fixed. Panel init command traces are practical integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/hw/mmp_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Kconfig

## Purpose
Defines the TPO HVGA panel driver option for the MMP display subsystem.

## Important APIs, Types, and Functions
- `config MMP_PANEL_TPOHVGA` is a bool depending on `SPI_MASTER`.

## Control Flow
Kconfig exposes support for the TPO TJ032MD01BW panel when SPI master support is available.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Controls compilation of the SPI panel driver that registers an MMP panel and uses SPI writes for power/init.

## Risks
The option depends only on `SPI_MASTER`; it assumes the enclosing MMP display menu and platform data provide a compatible SPI device and path.

## Test Signals
Build with SPI master enabled and verify the panel object is selectable and compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Makefile

## Purpose
Builds the TPO TJ032MD01BW MMP panel driver.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_MMP_PANEL_TPOHVGA) += tpo_tj032md01bw.o`.

## Control Flow
Kbuild compiles the panel driver when the Kconfig option is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Connects the MMP SPI panel source into the kernel build.

## Risks
None beyond config dependency correctness.

## Test Signals
Build with `CONFIG_MMP_PANEL_TPOHVGA=y` and verify object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/tpo_tj032md01bw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/tpo_tj032md01bw.c

## Purpose
Implements an SPI-controlled TPO TJ032MD01BW HVGA active panel driver for the MMP display subsystem. It registers a panel, provides one 320x480 mode, and sends power-on/off command sequences over SPI.

## Important APIs, Types, and Functions
- `init[]` and `poweroff[]` are 16-bit command sequences sent to the panel.
- `struct tpohvga_plat_data` stores platform power callback and SPI device pointer.
- `tpohvga_onoff()` toggles platform power and writes init or poweroff SPI commands.
- `mmp_modes_tpohvga[]` defines a 320x480 60 Hz RGB565 output mode with 10.3944 MHz pixel clock.
- `tpohvga_get_modelist()` returns the static mode list.
- `panel_tpohvga` is the `struct mmp_panel` registered with the MMP core.
- `tpohvga_probe()` validates platform data, sets SPI word size to 16, allocates panel private data, fills panel fields, and calls `mmp_register_panel()`.

## Control Flow
SPI core probes devices named `tpo-hvga`. The driver requires `struct mmp_mach_panel_info` platform data containing path name and platform on/off callback. It configures 16-bit SPI words, stores the SPI device and callback, binds the panel to the platform path name, and registers it. When a display path powers on the panel, `tpohvga_onoff()` calls platform power on then sends the init array. Power off sends the poweroff command then calls platform power off.

## State and Persistence
The driver uses one static `panel_tpohvga` object and allocates one `tpohvga_plat_data` in probe. Panel mode and command arrays are static. There is no remove callback, so allocated panel data and registration are not released on device removal.

## Dependencies and Integration Points
Depends on Linux SPI, platform data from `<video/mmp_disp.h>`, and MMP core panel registration. It can use the LCD-controller SPI master from `mmp_spi.c` or another SPI host with matching platform device setup.

## Risks
The static panel object and no remove path make multiple panel instances or hot-unplug unsafe. `tpohvga_onoff()` assumes `plat_onoff` is valid. Power-on sequencing has no delay between platform power and SPI init besides what lower layers may provide. SPI write failures are warnings only, so path power state may proceed despite panel init failure.

## Test Signals
Validate SPI probe with missing and valid platform data, 16-bit `spi_setup()`, panel registration and path name matching, mode list retrieval, power-on command sequence, power-off command, and warning logs on SPI transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/mmp/panel/tpo_tj032md01bw.c -->
