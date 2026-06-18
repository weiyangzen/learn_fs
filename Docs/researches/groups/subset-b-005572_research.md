# subset-b-005572 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/fbdev.c

## Purpose
`fbdev.c` is the Linux fbdev-facing RIVA/TNT/GeForce framebuffer driver. It binds supported NVIDIA PCI devices, maps MMIO and framebuffer apertures, discovers EDID, initializes the shared RIVA hardware abstraction, registers `struct fb_info`, and implements fbdev operations for mode setting, palette programming, panning, blanking, acceleration, cursor, open/release state save and restore, and module parameters.

## Important APIs, types, and functions
- `rivafb_pci_tbl`, `rivafb_driver`, `rivafb_probe()`, `rivafb_remove()`, `rivafb_init()`, and `rivafb_exit()` form the PCI/module lifecycle.
- `riva_fb_ops` wires fbdev callbacks: `rivafb_open`, `rivafb_release`, `rivafb_check_var`, `rivafb_set_par`, `rivafb_setcolreg`, `rivafb_pan_display`, `rivafb_blank`, accelerated `fillrect`/`copyarea`/`imageblit`, hardware cursor, sync, mmap, and I/O helpers.
- `riva_load_video_mode()` converts `fb_var_screeninfo` timings to VGA CRTC fields plus `RIVA_HW_STATE`, then calls `CalcStateExt()` and `riva_load_state()`.
- `riva_save_state()` and `riva_load_state()` bridge VGA register arrays in `struct riva_regs` with extended state callbacks from `riva_hw.c`.
- `riva_get_EDID_OF()`, `riva_get_EDID_i2c()`, `riva_get_edidinfo()`, and `riva_update_default_var()` derive monitor modes from firmware or DDC.
- Optional backlight support registers a raw backlight device and writes PMC/PCRTC backlight registers.

## Control flow
Probe removes conflicting apertures, allocates `fb_info` plus `struct riva_par`, enables PCI, claims BARs, maps control registers, computes architecture from PCI IDs, sets PRAMIN/PCRTC pointers, calls `riva_common_setup()`, measures VRAM and dclk, maps framebuffer memory write-combined, reads EDID, normalizes initial fb info, registers the framebuffer, and optionally initializes backlight. Mode changes flow through `rivafb_check_var()` for depth/timing validation and virtual-size clamping, then `rivafb_set_par()` unlocks VGA/RIVA registers, calls `riva_load_video_mode()`, resets acceleration and cursor state, and updates `fix` fields.

## State and persistence behavior
Persistent runtime state lives in `struct riva_par`: initial/current VGA plus extended RIVA state, X86 VGA save state, palette caches, EDID pointer, selected CRTC/flat-panel flags, write-combining cookie, cursor reset, and open reference count. Hardware state is saved on first open and restored on last release; remove tears down I2C, backlight, mappings, PCI regions, and allocations. Module parameters (`noaccel`, `flatpanel`, `forceCRTC`, `nomtrr`, `strictmode`, boot mode option, backlight) alter global driver behavior.

## Dependencies and integration points
This file depends on fbdev core, PCI, aperture conflict removal, Open Firmware EDID, optional I2C DDC via `rivafb-i2c.c`, optional PowerMac/backlight hooks, VGA save/restore on X86, and the RIVA hardware abstraction in `riva_hw.c`/`riva_hw.h`. Acceleration writes FIFO method registers defined in `riva_hw.h`; mode calculations rely on `CalcStateExt()`.

## Risks and test signals
Risk areas include legacy direct MMIO/VGA programming, unchecked hardware FIFO waits, mode validation shortcuts when monitor specs are incomplete, hardware cursor endian/packing paths, cleanup on partial probe failures, and known text-mode restore/doublescan issues. Test signals are successful PCI probe/unbind, fbcon display, EDID-derived mode selection, `fbset` mode changes across 8/16/32 bpp, pan/blank behavior, accelerated console scroll/fill/image paths, cursor visibility, suspend-like open/release restore on X86, and I2C/backlight operation when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_driver.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_driver.c

## Purpose
`nv_driver.c` is the RIVA driver's chip setup helper. It translates PCI/chipset state into initialized `RIVA_HW_INST` register-window pointers and display-head selection, detects VRAM size and maximum dot clock, and invokes the low-level RIVA configuration layer.

## Important APIs, types, and functions
- `riva_common_setup()` initializes MMIO sub-block pointers (`PRAMDAC0`, `PFB`, `PFIFO`, `PGRAPH`, `PEXTDEV`, `PTIMER`, `PMC`, `FIFO`, VGA I/O windows), selects CRTC/DAC register bases, autodetects flat panel/second CRTC where possible, and calls `RivaGetConfig()`.
- `riva_get_memlen()` returns VRAM size in KiB for NV3/NV4/NV10+ families, including integrated GeForce/nForce special cases that read host bridge PCI config.
- `riva_get_maxdclk()` derives a safe maximum dclk from memory/register characteristics.
- `riva_is_connected()`, `riva_is_second()`, and `riva_override_CRTC()` probe analog outputs and resolve second-head/forced CRTC decisions.

## Control flow
`fbdev.c` maps BARs and architecture-specific PRAMIN/PCRTC bases, then calls `riva_common_setup()`. This file fills the remaining register base pointers, determines VGA color/mono base from `MISCin()`, applies laptop flat-panel defaults, probes or forces second CRTC, selects active `PCIO`, `PCRTC`, `PRAMDAC`, and `PDIO` aliases, finalizes `flatPanel`, and lets `RivaGetConfig()` install architecture callbacks and FIFO object pointers.

## State and persistence behavior
The code mutates `struct riva_par` and embedded `RIVA_HW_INST`: MMIO pointers, `FlatPanel`, `SecondCRTC`, `forceCRTC`, chip memory/dclk characteristics, and two-head flags. No disk persistence exists. The output-detection routines temporarily write PRAMDAC probe registers, restore saved values, and delay for hardware settling.

## Dependencies and integration points
It includes `nv_type.h`, `rivafb.h`, and `nvreg.h`, uses PCI helper APIs for integrated chipset configuration, and depends on mapped control registers from `fbdev.c`. Its initialized pointers and callbacks are consumed by mode setting, acceleration, cursor, and state-save paths.

## Risks and test signals
Risks include brittle chipset ID heuristics, possible NULL PCI device results for integrated bridge lookups, invasive analog-output probing, forced CRTC misconfiguration, and divergent flat-panel defaults by platform. Test signals include correct VRAM reporting, correct framebuffer size, successful mode set on single-head and laptop panels, module parameter `forceCRTC` behavior, nForce/integrated memory sizing, and no register corruption after failed connector probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_type.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_type.h

## Purpose
`nv_type.h` centralizes legacy NVIDIA chipset constants as packed vendor/device IDs. It lets the driver compare `par->Chipset` against named `NV_CHIP_*` macros instead of scattering raw PCI IDs.

## Important APIs, types, and functions
The file exports preprocessor constants only. Important groups include RIVA 128/TNT/TNT2, GeForce/GeForce2/GeForce3/GeForce4 variants, Quadro variants, laptop/mobile IDs, integrated GeForce2/nForce IDs, and several raw `0x018*`/`0x028*` placeholders. It includes no functions or storage.

## Control flow
There is no runtime control flow in this header. At compile time, consumers such as `nv_driver.c` and `riva_hw.c` use these macros in switch/if logic for memory sizing, arbitration, two-head support, mobile flat-panel defaults, and integrated chipset handling.

## State and persistence behavior
No mutable state exists. The constants define the identity contract between PCI probing in `fbdev.c`, setup in `nv_driver.c`, and configuration in `riva_hw.c`.

## Dependencies and integration points
The macros depend on Linux PCI vendor/device ID definitions being available before or through including translation units. Integration points are direct equality checks against `(vendor << 16) | device`, especially `NV_CHIP_IGEFORCE2`, `NV_CHIP_0x01F0`, `NV_CHIP_GEFORCE2_GO`, and RIVA/TNT families.

## Risks and test signals
Risks are stale or mismatched PCI names, inconsistent aliases (`QUADRO_DCC` vs table naming), and missing newer variants. Test signals are successful compilation against current PCI ID headers and correct architecture/setup selection for every PCI ID in `rivafb_pci_tbl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nv_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nvreg.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nvreg.h

## Purpose
`nvreg.h` is a legacy macro layer for NVIDIA register bitfields and device register access. In this kernel driver it primarily supplies bitfield helpers used by `fbdev.c` timing construction, while much of the older direct `nvCONTROL`/port-I/O macro surface remains as compatibility baggage from XFree86-era code.

## Important APIs, types, and functions
- `BITMASK`, `MASKEXPAND`, `SetBF`, `GetBF`, and `MaskAndSetBF` implement compile-time bitfield packing/unpacking for mask expressions such as `8:8`.
- `DEVICE_*` and per-device wrappers (`PFB_*`, `PRAMDAC_*`, `PFIFO_*`, etc.) address an external `nvCONTROL` aperture.
- `CRTC_*`, `PCRTC_*`, and `SR_*` wrap legacy port I/O.
- `NVChipType` and `GetChipType()` are declared but not used by the modern fbdev files in this subset.

## Control flow
There is no normal runtime control flow beyond macro expansion. `fbdev.c` uses `SetBF`/`GetBF` through local wrappers to construct overflow bits in VGA CRTC timing registers and extended screen/horizontal fields.

## State and persistence behavior
No owned runtime state exists, but the macros can read and write hardware registers when used. The declared global `nvCONTROL` would be a process/global MMIO base in older code; this subset's active RIVA paths use `NV_RD32`/`NV_WR32` from `riva_hw.h` instead.

## Dependencies and integration points
Integration is mostly compile-time: `fbdev.c` includes this header for bitfield helpers, and older register names may still document intended hardware blocks. It depends on the C preprocessor's treatment of `x:y` macro arguments and on architecture port I/O helpers if the legacy macros are ever used.

## Risks and test signals
Risks include confusing dead/legacy macros, typo `PTIEMR` in `PTIMER_Val`, duplicate `PMC_*` definitions, unsafe side effects in assignment macros, and portability issues with raw port I/O. Test signals are clean builds with all call sites, correct computed CRTC overflow fields in mode tests, and static analysis confirming unused legacy macros do not hide active bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/nvreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.c

## Purpose
`riva_hw.c` is the low-level hardware abstraction for NV3/NV4/NV10-family RIVA chips. It hides architecture-specific register programming behind `RIVA_HW_INST` callbacks, computes PLL and FIFO arbitration values for a requested mode, loads fixed-function PRAMIN/PFIFO/PGRAPH state, saves/restores extended mode state, and initializes chip configuration.

## Important APIs, types, and functions
- Exported APIs: `CalcStateExt()` calculates `RIVA_HW_STATE` from bpp, virtual width, display size, height, and dot clock; `RivaGetConfig()` fills chip configuration and callback pointers.
- State callbacks installed into `RIVA_HW_INST`: `LoadStateExt`, `UnloadStateExt`, `SetStartAddress`, `SetSurfaces2D`, `SetSurfaces3D`, `ShowHideCursor`, `LockUnlock`, and `Busy`.
- Arbitration families: `nv3CalcArbitration`, `nv4CalcArbitration`, `nv10CalcArbitration`, update wrappers, and `nForceUpdateArbitrationSettings()`.
- Configuration functions: `nv3GetConfig()`, `nv4GetConfig()`, `nv10GetConfig()`.

## Control flow
On setup, `RivaGetConfig()` selects an architecture-specific config function, derives RAM/crystal/vblank/cursor details, assigns callbacks, then maps FIFO method object pointers. On mode set, `CalcStateExt()` computes PLL M/N/P, arbitration watermarks, cursor location/config, pixel format, pitch, repaint, offset, flat-panel/two-head fields, and returns a filled state. `LoadStateExt()` writes common fixed tables, architecture tables from `riva_tbl.h`, bpp-specific tables, offsets/pitches, two-head/flat-panel state, PRAMDAC PLL/scale/general registers, interrupt/vblank registers, and resets FIFO counters. `UnloadStateExt()` reads the inverse subset into `RIVA_HW_STATE`.

## State and persistence behavior
State is persisted only in memory and hardware registers. `RIVA_HW_INST` records chip capabilities, MMIO pointers, FIFO free/empty counts, current state pointer, cursor start, and function pointers. `RIVA_HW_STATE` snapshots mode registers and render surface pitch/offsets. Hardware writes are immediate and global to the device; no locking is provided inside this file beyond caller discipline.

## Dependencies and integration points
It depends on `riva_hw.h` for register access and object layouts, `riva_tbl.h` for fixed register tables, `nv_type.h` for chipset tests, and Linux PCI helpers for integrated chipset memory/arbitration details. `fbdev.c` calls `CalcStateExt()` and uses the installed callbacks for mode loading, panning, cursor, acceleration waits, and state save/restore.

## Risks and test signals
Risks include opaque magic register tables, arithmetic overflow/divide-by-zero if clocks or PCI bridge reads are invalid, busy-wait loops, architecture-specific register drift, writing read-only/unknown registers during load, and fragile big-endian handling. Test signals include mode setting across NV3/NV4/NV10/NV20/NV30, stable accelerated blits after mode load, cursor placement, panning start address, flat-panel and two-head behavior, correct VRAM size/cursor offset, and no FIFO underrun/snow at high pixel clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.h

## Purpose
`riva_hw.h` defines the RIVA hardware abstraction contract: fixed-width types, raw MMIO/VGA access macros, architecture constants, memory-mapped FIFO method object layouts, the `RIVA_HW_INST` virtual chip object, the `RIVA_HW_STATE` mode snapshot, exported low-level functions, and FIFO availability macro.

## Important APIs, types, and functions
- Access macros: `NV_WR08/16/32`, `NV_RD08/16/32`, `VGA_WR08`, and `VGA_RD08`.
- Architecture constants: `NV_ARCH_03`, `NV_ARCH_04`, `NV_ARCH_10`, `NV_ARCH_20`, `NV_ARCH_30`, `NV_ARCH_40`.
- FIFO object structs: `RivaRop`, `RivaPattern`, `RivaClip`, `RivaRectangle`, `RivaScreenBlt`, `RivaPixmap`, `RivaBitmap`, `RivaTexturedTriangle03`, `RivaTexturedTriangle05`, `RivaLine`, `RivaSurface`, and `RivaSurface3D`.
- `RIVA_HW_INST` stores hardware capabilities, MMIO pointers, function pointers, current state, and FIFO object pointers.
- `RIVA_HW_STATE` stores extended mode fields such as PLLs, repaint, arbitration, cursor, pitch, offsets, dither, scale, and two-head owner state.
- `RIVA_FIFO_FREE()` waits for and consumes FIFO slots.

## Control flow
The header has no standalone control flow, but its function pointers define the runtime dispatch model used by the driver. `RivaGetConfig()` fills `RIVA_HW_INST`; fbdev callbacks then call generic methods such as `chip->Busy()` or `chip->SetStartAddress()` without knowing the architecture. FIFO writes in `fbdev.c` are guarded by `RIVA_FIFO_FREE()`.

## State and persistence behavior
The defined structs mirror live hardware state. `RIVA_HW_INST` persists for the lifetime of the framebuffer device inside `struct riva_par`; `RIVA_HW_STATE` instances hold initial/current mode state for restore and mode switches. `RIVA_FIFO_FREE()` mutates `FifoFreeCount`, so callers must treat it as shared state tied to FIFO submissions.

## Dependencies and integration points
This header depends on `asm/io.h` and Linux `__iomem` conventions. It is included by `rivafb.h`, `fbdev.c`, `nv_driver.c`, and `riva_hw.c`. The struct layouts must match NVIDIA FIFO method offsets consumed by hardware and by table initialization in `riva_tbl.h`.

## Risks and test signals
Risks include raw `__raw_*` MMIO ordering/endian semantics, volatile struct layout assumptions, unchecked infinite FIFO waits, float fields in MMIO method structs, and architecture register layout mismatch. Test signals are compile-time sparse/checker cleanliness for `__iomem`, successful accelerated operations, no FIFO deadlocks under console stress, and correct behavior on big-endian configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_tbl.h

## Purpose
`riva_tbl.h` contains static fixed-function initialization tables for RIVA/NVIDIA hardware blocks. The tables encode register offset/value pairs loaded by `riva_hw.c` during mode setup to initialize PMC, PTIMER, FIFO, PFIFO, PRAMIN, and PGRAPH state for NV3, NV4, and NV10-family chips.

## Important APIs, types, and functions
There are no functions; the API is the table names consumed by `LOAD_FIXED_STATE*` macros in `riva_hw.c`. Important tables include common `RivaTablePMC`, `RivaTablePTIMER`, `RivaTableFIFO`; NV3 `nv3TablePFIFO`, `nv3TablePGRAPH`, `nv3TablePRAMIN` plus 8/15/32 bpp variants; NV4 `nv4TableFIFO/PFIFO/PGRAPH/PRAMIN` plus 8/15/16/32 bpp variants; NV10 equivalents plus `nv10tri05TablePGRAPH` and big-endian conditional values.

## Control flow
No direct control flow exists. Runtime selection happens in `LoadStateExt()`: it writes common tables, then architecture-specific tables, then bpp-specific tables. `UpdateFifoState()` also uses NV4/NV10 FIFO and triangle tables after mode load.

## State and persistence behavior
The arrays are static read-only driver data in practice, although not declared `const`. They become persistent hardware state only when copied into registers. The bpp-specific PRAMIN/PGRAPH tables encode object formats and mono expansion behavior for acceleration.

## Dependencies and integration points
This file is included directly by `riva_hw.c`; table names are coupled to token-pasting macros such as `LOAD_FIXED_STATE(nv10,PGRAPH)`. The values depend on the FIFO object layouts from `riva_hw.h` and the architecture-specific load order in `LoadStateExt()`.

## Risks and test signals
Risks include magic values with little local explanation, mutable static arrays, architecture/bpp table omissions, big-endian conditional coverage, and tight name coupling to macros. Test signals are successful mode load for each supported bpp and architecture, working ROP/fill/blit/image acceleration, and no PGRAPH/PFIFO faults after repeated mode switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/riva_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb-i2c.c

## Purpose
`rivafb-i2c.c` provides bit-banged I2C/DDC support for the RIVA framebuffer driver. It exposes up to three DDC busses through Linux `i2c-algo-bit`, allowing `fbdev.c` to read monitor EDID blocks via `fb_ddc_read()`.

## Important APIs, types, and functions
- GPIO callbacks `riva_gpio_setscl()`, `riva_gpio_setsda()`, `riva_gpio_getscl()`, and `riva_gpio_getsda()` manipulate VGA CRTC-indexed DDC bits.
- `riva_setup_i2c_bus()` initializes one `struct riva_i2c_chan` adapter and registers it with `i2c_bit_add_bus()`.
- Exported helpers `riva_create_i2c_busses()`, `riva_delete_i2c_busses()`, and `riva_probe_i2c_connector()` are called from probe/remove/EDID discovery in `fbdev.c`.

## Control flow
`riva_create_i2c_busses()` attaches `par` to three channels, assigns DDC base indices `0x36`, `0x3e`, and `0x50`, and registers BUS1/BUS2/BUS3. Bus setup raises SDA/SCL, delays, and hands callbacks to the I2C bit-bang core. EDID probing checks whether the requested channel registered, reads EDID, returns it via `out_edid`, and reports success as `0` when an EDID buffer was returned.

## State and persistence behavior
Per-channel state lives in `struct riva_i2c_chan`: parent `par`, DDC base index, `i2c_adapter`, and bit algorithm data. Failed registration sets `chan->par = NULL`; deletion unregisters live adapters and clears the pointer. EDID buffers are allocated by `fb_ddc_read()` and freed by the caller path in `fbdev.c`.

## Dependencies and integration points
The file depends on `rivafb.h`, Linux I2C core, `i2c-algo-bit`, fbdev EDID helper `../edid.h`, VGA register access macros, and the active `par->riva.PCIO` CRTC window selected by `nv_driver.c`. It is compiled only when RIVA I2C support is enabled.

## Risks and test signals
Risks include no explicit locking around shared CRTC index/data registers, fixed DDC base guesses, inverted success convention in `riva_probe_i2c_connector()` relative to some kernel style, and possible bus leaks if partial creation is not deleted. Test signals include three adapter registrations, successful EDID read on expected connectors, clean deletion on remove and probe failure, and no interference with mode-setting CRTC accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb.h -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb.h

## Purpose
`rivafb.h` is the shared private header for the RIVA fbdev driver. It defines VGA register-count constants, DDC bit masks, saved mode structures, I2C channel state, the main per-device `struct riva_par`, and cross-file prototypes.

## Important APIs, types, and functions
- `struct riva_regs` stores VGA attribute, CRTC, graphics, sequencer, misc output, and `RIVA_HW_STATE` extended registers.
- `struct riva_i2c_chan` stores the bit-banged DDC adapter, algorithm data, DDC base, and back-pointer.
- `struct riva_par` stores the embedded `RIVA_HW_INST`, pseudo/direct palettes, MMIO base, dclk limit, initial/current states, optional X86 VGA state, open lock/refcount, EDID pointer, chipset/flat-panel/CRTC flags, PCI device, cursor reset, write-combining cookie, and three I2C channels.
- Prototypes connect `nv_driver.c`, `rivafb-i2c.c`, and `riva_hw.c` to `fbdev.c`.

## Control flow
The header defines data contracts rather than executable flow. `fbdev.c` allocates `struct riva_par` inside `fb_info`, `nv_driver.c` fills hardware pointers/configuration, `riva_hw.c` mutates `RIVA_HW_INST` and extended states, and `rivafb-i2c.c` manages `chan[]`.

## State and persistence behavior
`struct riva_par` is the driver's primary persistent in-memory state for a bound PCI device. It survives from successful probe until remove, with mode state additionally saved/restored across open/release transitions. No state is written outside memory/hardware.

## Dependencies and integration points
It includes fbdev, VGA, I2C, I2C bit-bang, and `riva_hw.h`. Integration points are broad: every source in the RIVA subset shares this header, and its struct layout must remain consistent with allocation in `framebuffer_alloc()` and use in fbdev callbacks.

## Risks and test signals
Risks include lifetime ownership ambiguity for `EDID`, conditional `vgastate` fields, shared channel array state, and stale DDC mask macros not used by the bit-bang implementation. Test signals include clean builds under combinations of `CONFIG_X86` and `CONFIG_FB_RIVA_I2C`, successful probe/remove without leaks, and correct state restore after last framebuffer close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/rivafb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s1d13xxxfb.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/s1d13xxxfb.c

## Purpose
`s1d13xxxfb.c` is a platform framebuffer driver for Epson S1D13xxx display controllers. It maps externally supplied VRAM/register resources, optionally runs platform-provided register initialization, discovers current LCD/CRT hardware state, registers fbdev operations, and provides basic color, blanking, panning, and S1D13506 bitblt acceleration.

## Important APIs, types, and functions
- Platform lifecycle: `s1d13xxxfb_probe()`, `s1d13xxxfb_remove()`, `s1d13xxxfb_init()`, `s1d13xxxfb_exit()`, and optional PM `s1d13xxxfb_suspend()`/`s1d13xxxfb_resume()`.
- Register helpers: `s1d13xxxfb_readreg()`, `s1d13xxxfb_writereg()`, `s1d13xxxfb_runinit()`, `lcd_enable()`, and `crt_enable()`.
- fbdev callbacks: `s1d13xxxfb_set_par()`, `s1d13xxxfb_setcolreg()`, `s1d13xxxfb_blank()`, and `s1d13xxxfb_pan_display()`.
- Acceleration: `s1d13xxxfb_bitblt_copyarea()`, `s1d13xxxfb_bitblt_solidfill()`, and `bltbit_wait_bitclear()`, selected for S1D13506.
- `s1d13xxxfb_fetch_hw_state()` translates existing chip registers into `fb_var_screeninfo` and `fb_fix_screeninfo`.

## Control flow
Probe optionally calls platform video init, validates two memory resources, claims and maps VRAM/registers, reads production/revision ID, selects fbops based on chip ID, runs platform init register scripts, fetches current hardware mode, and registers the framebuffer. `set_par` changes display bpp bits for LCD or CRT and updates line length. `blank` toggles LCD/CRT enable bits. `pan_display` writes display start registers from `yoffset`. Acceleration programs bitblt source/destination/size/ROP registers under a spinlock and waits for the start bit to clear.

## State and persistence behavior
Driver state lives in `struct s1d13xxxfb_par` allocated with `fb_info`: register base, pseudo palette, chip ID/revision, display flags, and PM save buffers. Hardware register state may originate from firmware/platform init and is mirrored into fbdev structures by `fetch_hw_state`. Suspend saves registers into `regs_save`, optionally display memory if enabled in code, powers down, and resume restores registers/framebuffer and output enables.

## Dependencies and integration points
The driver depends on platform devices/resources, `video/s1d13xxxfb.h` register definitions and platform data (`initregs`, platform suspend/resume hooks), fbdev core, MMIO helpers, and generic cfb imageblit for the accelerated variant. It has no PCI discovery of its own; board/platform code supplies resources and initialization.

## Risks and test signals
Risks include missing `check_var()` despite set_par assumptions, TODO-noted SMP safety concerns, partial probe cleanup that releases both resources even if the second claim failed, accelerated wait timeouts without error propagation, no xoffset panning, limited bpp/mode support, and PM writing back read-only registers. Test signals include platform probe with valid resources, correct chip ID matching, mode geometry matching firmware/init registers, palette writes in pseudo and truecolor modes, LCD/CRT blank/unblank, ypan through fbcon, S1D13506 fill/copy acceleration under overlapping copies, suspend/resume register restoration, and clean remove after failed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/s1d13xxxfb.c -->
