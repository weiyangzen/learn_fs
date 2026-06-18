# Research: subset-b-003665

Grouped source research for subset B work item `subset-b-003665`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c

## Purpose
This file creates and tears down the pre-NV50 Nouveau KMS display stack. It wires `nv04_display` into `nouveau_display`, creates CRTCs and encoders from VBIOS DCB outputs, saves/restores legacy mode state, manages suspend/resume framebuffer and cursor pinning, and enables flip-completion events.

## Important APIs, Types, and Functions
`nv04_display_create` is the public constructor. `nv04_display_init`, `nv04_display_fini`, and `nv04_display_destroy` become display lifecycle callbacks. `nv04_encoder_get_connector` maps a Nouveau encoder back to its attached connector. The file depends on `struct nv04_display`, `struct nouveau_encoder`, `struct nouveau_crtc`, DCB output entries, `nvif_event`, and GEM/BO helpers.

## Control Flow
Creation allocates `nv04_display`, disables atomic DRM ioctls for pre-NV50 hardware, creates an optional flip event on the channel software object, saves VGA fonts, instantiates one or two CRTCs, then walks DCB outputs to create DAC, DFP, on-chip TV, or external TV encoders. Connectors without encoders are removed, I2C buses are attached to encoders by DCB index, initial CRTC and encoder state is saved, and overlay planes are initialized. Resume init re-saves preexisting state, allows flip events, repins framebuffer and cursor BOs, invalidates LUT depth for reload, and forces modes unless runtime resume avoids modeset locking. Fini blocks flip events, disables vblank interrupts, cancels HPD work outside runtime suspend, and on suspend unpins scanout/cursor BOs. Destroy restores encoder/CRTC state, restores VGA fonts, destroys the flip event, and frees display private state.

## State and Persistence Behavior
Persistent state lives in `nouveau_display(dev)->priv`, `nv04_display.mode_reg`, `saved_reg`, `saved_vga_font`, per-CRTC cursor BO mappings, primary framebuffer BO pin state, and `disp->flip`. Suspend intentionally releases VRAM pins so memory can migrate; resume re-establishes pins and cursor mapping/position.

## Dependencies and Integration Points
The file integrates with DRM connector/encoder/CRTC lists, Nouveau DCB parsing, `nv04_crtc_create`, DAC/DFP/TV constructors, `nouveau_overlay_init`, GEM BO pin/map/unpin, `drm_helper_resume_force_mode`, HPD work, and NVIF software event delivery through `nv04_flip_complete`.

## Risks
Errors after `vzalloc` and before full teardown can leak partially initialized state if callers do not unwind display creation. BO pin failures during resume are logged but not fatal, so scanout may resume with broken framebuffer or cursor state. The initialization still relies on saved firmware/pre-driver register state, which is fragile across suspend and head ownership quirks. Connector pruning depends on `possible_encoders` being set correctly by encoder constructors.

## Test Signals
Useful signals include boot and module reload on NV04-NV4x GPUs, DCB coverage for analog, TMDS/LVDS, on-chip TV, and external TV outputs, suspend/resume with active framebuffer and cursor, runtime resume through connector wake, page-flip completion events, vblank interrupt suppression, and connector list cleanup for unsupported DCB outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h

## Purpose
This header defines the shared pre-NV50 display state and declares the CRTC, encoder, TV, overlay, and helper entry points used across `dispnv04`.

## Important APIs, Types, and Functions
Key data structures are `enum nv04_fp_display_regs`, `struct nv04_crtc_reg`, `struct nv04_output_reg`, `struct nv04_mode_state`, and `struct nv04_display`. It declares creation functions such as `nv04_display_create`, `nv04_crtc_create`, `nv04_dac_create`, `nv04_dfp_create`, `nv04_tv_create`, and `nv17_tv_create`, plus helper functions for FP binding, DAC clock/load detection, overlay init, BIOS init-table execution, and flip events. Inline hardware-family helpers include `nv_two_heads`, `nv_gf4_disp_arch`, `nv_two_reg_pll`, and `nv_match_device`.

## Control Flow
The header has no standalone execution, but its inline helpers drive many hardware-condition branches. `nv_two_heads` gates dual-head paths based on PCI device and family, `nv_gf4_disp_arch` selects GF4-style register layout, `nv_two_reg_pll` selects PLL decode/programming paths, and `nouveau_bios_run_init_table` invokes `nvbios_init` with output and head context.

## State and Persistence Behavior
`struct nv04_crtc_reg` is a full save/restore snapshot of VGA, PCRTC, PRAMDAC, TV, flat-panel, dither, cursor, and CTV registers. `struct nv04_display` persists current and saved mode state, VGA font planes, DAC user accounting, image BOs, the flip event object, and the owning DRM client pointer.

## Dependencies and Integration Points
It pulls in Nouveau display core state, BIOS PLL/init helpers, NVIF events, DCB output types, and PCI device checks. Most NV04 CRTC, DAC, DFP, TV, and overlay files share this header as their state contract.

## Risks
The large register snapshots must stay aligned with save/load code in `hw.c` and encoder files; missing fields cause incomplete restore. Family predicates encode chipset exceptions and can break unusual PCI IDs. The BIOS init wrapper relies on compound-literal style macro arguments to `nvbios_init`, so signature drift is build-sensitive.

## Test Signals
Build coverage across all `dispnv04` objects is the first signal. Runtime signals include correct dual-head detection, PLL programming on NV30/NV40 families, BIOS init-table execution for all output types, suspend/resume register restore, and flip-event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c

## Purpose
This file implements low-level NV04-NV4x display register access, PLL reading, clock derivation, VGA font preservation, and full display mode state save/load for legacy VGA, CRTC, RAMDAC, palette, flat-panel, TV, cursor, and overlay-related registers.

## Important APIs, Types, and Functions
Public helpers include `NVWriteVgaSeq`, `NVReadVgaSeq`, `NVWriteVgaGr`, `NVReadVgaGr`, `NVSetOwner`, `NVBlankScreen`, `nouveau_hw_get_pllvals`, `nouveau_hw_pllvals_to_clk`, `nouveau_hw_get_clock`, `nouveau_hw_save_vga_fonts`, `nouveau_hw_save_state`, `nouveau_hw_load_state`, and `nouveau_hw_load_state_palette`. Internal helpers decode PLLs, save/load RAMDAC/VGA/extended/palette state, and work around bad unused-head VPLL values.

## Control Flow
Register access wrappers program VGA index/data pairs through PRMVIO. `NVSetOwner` writes CR44 and special NV11 dummy registers to select the active VGA owner. PLL queries parse VBIOS PLL limits, read the appropriate one- or two-register coefficients, handle Celsius single-stage VPLL state, and decode coefficients into `nvkm_pll_vals`. Clock reads special-case nForce memory clocks through PCI config space. VGA font save/restore maps the first 64 KiB of VRAM, blanks displays, programs VGA planes, copies four 16 KiB font planes, and restores VGA control registers.

Mode save calls RAMDAC, VGA, palette, and extended-save routines after fixing bad NV11 VPLLs. Mode load protects VGA output, programs PLL/RAMDAC state, resets PVIDEO and limits, restores extended CRTC, palette, and VGA registers, waits for retrace before some GF4 register writes, then unprotects VGA.

## State and Persistence Behavior
The file serializes hardware state into `struct nv04_mode_state` and `struct nv04_crtc_reg`, including PLL coefficients, palette bytes, cursor config, TV timings, FP timings, CTV registers, and saved framebuffer start offsets. It mutates hardware registers directly and persists VGA fonts in `nv04_display.saved_vga_font`.

## Dependencies and Integration Points
It depends on `nvif_rd/wr` MMIO helpers, NVIF timer waits, VBIOS PLL parsing, Nouveau clock PLL programming, `nv04_display` state, PCI config access, and register constants from `nvreg.h`. CRTC, DFP, TV, cursor, and display lifecycle code call these helpers during modeset, save/restore, suspend, and unload.

## Risks
This code touches many undocumented registers and contains chipset-specific ordering requirements; wrong ordering can lock hardware. Palette and font access require VGA attribute flip-flop handling and correct head ownership. PLL decode can return zero clocks if called before coefficients are valid. VGA font mapping assumes BAR/resource layout and text mode. PVIDEO reset during state load can disrupt overlay state if sequencing changes.

## Test Signals
Signals include register save/load round trips, text-console font preservation, dual-head owner switching, suspend/resume on NV11/NV30/NV40, PLL clock reporting versus expected VBIOS limits, palette restore, overlay disable after modeset, and stress around GF4 retrace waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h

## Purpose
This header exposes the pre-NV50 display hardware helper API and defines inline register accessors and bitfield helpers for CRTC, RAMDAC, VGA, PRMVIO, TMDS, cursor, and pitch operations.

## Important APIs, Types, and Functions
It declares the exported functions implemented in `hw.c` and `nouveau_calc_arb`. Inline APIs include `NVReadCRTC`, `NVWriteCRTC`, `NVReadRAMDAC`, `NVWriteRAMDAC`, `nv_read_tmds`, `nv_write_tmds`, VGA CRTC/attribute/PRMVIO accessors, `NVVgaSeqReset`, `NVVgaProtect`, `nv_heads_tied`, CRTC lock helpers, `NVLockVgaCrtcs`, `nv_cursor_width`, `nv_fix_nv40_hw_cursor`, `nv_set_crtc_base`, `nv_show_cursor`, and `nv_pitch_align`.

## Control Flow
The inline functions translate head numbers to register-window offsets, maintain VGA attribute controller enable state, switch PRMVIO addressing only where NV4x exposes per-head ranges, and update CRTC shadow/lock bits. Cursor helpers update saved mode state and kick NV40 cursor position when needed. Pitch alignment computes chipset-dependent width alignment from bits per pixel.

## State and Persistence Behavior
The header mutates hardware registers and `nv04_display(dev)->mode_reg` through inline helpers. It does not own storage except through the referenced display state, but callers rely on the helpers to keep software register snapshots and actual hardware in sync.

## Dependencies and Integration Points
It includes `disp.h`, `nvreg.h`, PLL BIOS declarations, and uses `nouveau_drm(dev)->client.device.object` for NVIF MMIO. It is the common hardware access layer for NV04 CRTC, DFP, DAC, TV, overlay, and mode-state code.

## Risks
Because much of the API is inline, incorrect use can bypass required head ownership or lock/protect sequencing. Bitfield macros rely on the local `high:low` macro idiom and are not type-safe. PRMVIO per-head behavior differs before NV4x, and callers must call `NVSetOwner` where required. Cursor visibility changes touch saved state and hardware, so missed synchronization can produce stale cursor state.

## Test Signals
Compile coverage catches register macro drift. Runtime signals include CRTC register access on both heads, palette state preservation, cursor show/hide and base changes on NV04/NV10/NV40, pitch alignment for common bpp values, TMDS indirect register reads/writes, and lock/unlock correctness around modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild

## Purpose
This build fragment defines optional external I2C encoder modules for pre-NV50 Nouveau display support.

## Important APIs, Types, and Functions
It declares `ch7006-y` as `ch7006_drv.o` plus `ch7006_mode.o`, adds it when `CONFIG_DRM_NOUVEAU_CH7006` is enabled, declares `sil164-y` as `sil164_drv.o`, and adds it when `CONFIG_DRM_NOUVEAU_SIL164` is enabled.

## Control Flow
There is no runtime flow. Kbuild combines the listed objects into module/built-in targets selected by kernel configuration.

## State and Persistence Behavior
No runtime state is stored. The file determines whether CH7006 TV and SIL164 TMDS slave encoder support is available to `request_module` and Nouveau's I2C encoder creation path.

## Dependencies and Integration Points
It integrates with the parent Nouveau Kbuild, Kconfig symbols, and the external encoder bridge in `nouveau_i2c_encoder.c`.

## Risks
If config symbols are disabled, DCB entries requiring those external encoders cannot bind. Object list changes must stay synchronized with exported symbols across driver and mode files.

## Test Signals
Build with both symbols enabled, disabled, built-in, and modular. Runtime probe of CH7006 and SIL164 DCB outputs verifies the objects were linked and module autoload names match I2C board info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_drv.c

## Purpose
This file implements the I2C driver and Nouveau encoder callbacks for the Chrontel CH7006 external TV encoder.

## Important APIs, Types, and Functions
It defines `ch7006_encoder_funcs`, module parameters `debug`, `tv_norm`, and `scale`, the I2C `ch7006_driver`, and callbacks for config, destroy, DPMS, save/restore, mode fixup/valid/set, detection, mode listing, TV property creation, and TV property updates. `ch7006_probe`, `ch7006_resume`, and `ch7006_encoder_init` are the core I2C lifecycle hooks.

## Control Flow
Probe reads `CH7006_VERSION_ID`, logs it, and writes register `0x3d` to enable signal output. Encoder init allocates private state, installs the callback table, chooses defaults and module-parameter overrides, and records chip version. Mode fixup/validation accepts only table-driven modes from `ch7006_lookup_mode`. Mode set fills the register shadow from TV norm, input format, clock/sync params, mode timing, subcarrier, PLL, power, and properties, then writes the full state over I2C. Detection temporarily powers and clocks the chip, triggers sense, reads detect bits, restores saved detect/power/clock registers, and updates DRM subconnector state. Property changes either live-update affected registers or force a mode reprobe for norm/scale changes that require DPMS off.

## State and Persistence Behavior
`struct ch7006_priv` stores current encoder parameters, current and saved register shadows, selected/actual subconnector, margins, norm, brightness/contrast/flicker/scale, chip version, last DPMS mode, and a custom scale property. Save/restore snapshots all relevant chip registers via `ch7006_state_save/load`.

## Dependencies and Integration Points
The file depends on DRM TV connector properties, Nouveau I2C encoder wrappers, `ch7006_mode.c` calculations, `ch7006_priv.h` register definitions, Linux I2C module registration, and external TV creation in `tvnv04.c`.

## Risks
The chip accepts only specific timing tables; custom modes fail. Several properties mutate hardware immediately and assume `priv->mode`/state is valid. Norm and scale changes while active are rejected, but reprobe/remodeset flow depends on helper callbacks. I2C errors are logged but register writes often continue, so partial programming can leave no signal. Detection disturbs power/clock registers temporarily.

## Test Signals
Probe on boards with CH7006, supported PAL/NTSC norms, scale 0/1/2 mode lists, subconnector detection for composite/S-video/SCART, DPMS transitions, suspend/resume reinitialization, property updates for brightness/contrast/flicker/margins, and invalid module parameter handling are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c

## Purpose
This file provides CH7006 TV norm tables, supported mode tables, mode lookup, and hardware register calculations for levels, subcarrier frequency, PLL programming, power state, position, contrast, and flicker filtering.

## Important APIs, Types, and Functions
It exports `ch7006_tv_norm_names`, `ch7006_tv_norms`, `ch7006_modes`, `ch7006_lookup_mode`, `ch7006_setup_levels`, `ch7006_setup_subcarrier`, `ch7006_setup_pll`, `ch7006_setup_power_state`, `ch7006_setup_properties`, `ch7006_write`, `ch7006_read`, `ch7006_state_load`, and `ch7006_state_save`.

## Control Flow
Mode tables describe PAL-like and NTSC-like timings with valid norm and scale masks. Lookup matches norm plus exact display geometry, totals, and clock. Setup functions compute DAC gain and black level from norm and brightness, split a calculated subcarrier increment across eight registers, brute-force CH7006 PLL `N/M` values against requested pixel clock, derive power bits from DPMS and subconnector choice, and compute horizontal/vertical positioning from overscan-like margins and aspect ratio. State load/save write/read registers in a defined order, with FFILTER bit reordering after save.

## State and Persistence Behavior
The file manipulates the caller-owned `struct ch7006_state` register array and `struct ch7006_priv` current mode/property state. No persistent kernel object is allocated here; hardware persistence is the CH7006 register set written over I2C.

## Dependencies and Integration Points
It depends on fixed-point helpers/macros in `ch7006_priv.h`, DRM mode definitions, I2C master send/receive, and the driver callbacks in `ch7006_drv.c`.

## Risks
The register calculations use fixed-point constants and table-derived coefficients; small arithmetic mistakes can produce invalid TV colorburst or positioning. PLL search is exhaustive but simple and assumes CH7006 frequency formula. I2C read failures return zero, which can be mistaken for real state. Unsupported norms/modes cannot be synthesized.

## Test Signals
Signals include exact mode lookup for every table entry, PAL/NTSC color output, PLL values close to requested clocks, brightness/contrast/flicker/margin changes on live output, save/restore fidelity, I2C error injection, and visual validation of subcarrier and color levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h

## Purpose
This private header defines CH7006 driver state, TV norm/mode structures, register constants, bitfield helpers, module parameter declarations, and function prototypes shared by the CH7006 driver and mode calculation files.

## Important APIs, Types, and Functions
Important types are `fixed`, `enum ch7006_tv_norm`, `struct ch7006_tv_norm_info`, `struct ch7006_mode`, `struct ch7006_state`, and `struct ch7006_priv`. It defines `to_ch7006_priv`, logging macros, bitfield macros `bitf`, `bitfs`, `setbitf`, `unbitf`, interpolation and fixed rounding helpers, register load/save macros, hardware constants `CH7006_FREQ0`, `CH7006_MAXN`, `CH7006_MAXM`, and register/field definitions through `CH7006_VERSION_ID`.

## Control Flow
The header has no standalone flow, but its macros implement all register field packing/unpacking used by `ch7006_mode.c`. `interpolate` maps 0-100 user property values around a midpoint, and `round_fixed` converts 32.32 fixed-point values.

## State and Persistence Behavior
`struct ch7006_priv` owns the persistent per-encoder software state: configuration parameters, current mode pointer, register shadows, saved hardware state, DRM scale property, TV properties, chip version, and last DPMS state. `struct ch7006_state` mirrors the hardware register space.

## Dependencies and Integration Points
It includes DRM probe helpers and public Nouveau I2C encoder/CH7006 parameter headers. It is internal to the CH7006 module and feeds the external TV path in `tvnv04.c` through callback registration.

## Risks
The bitfield macros use the same `high:low` preprocessor idiom as Nouveau register headers and are easy to misuse. The register array is sized to `0x26`; new register constants beyond that would overrun if added carelessly. Property defaults and module parameters must remain consistent with DRM TV property ranges.

## Test Signals
Compile coverage for every macro use, mode-set tests that exercise all register fields, static analysis for register-index bounds, module parameter parsing, and save/load round trips are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/ch7006_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/sil164_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/sil164_drv.c

## Purpose
This file implements the Silicon Image SIL164 external TMDS transmitter driver and Nouveau I2C encoder callbacks, including optional dual-link slave handling.

## Important APIs, Types, and Functions
It defines `struct sil164_priv`, SIL164 register constants, I2C access helpers, state save/restore, power and init helpers, the `sil164_encoder_funcs` callback table, `sil164_probe`, `sil164_detect_slave`, `sil164_encoder_init`, and the module init/exit functions.

## Control Flow
Probe validates vendor/device/revision registers. Encoder init allocates private state, installs callbacks, and probes a slave device at address `0x39` for dual-link support. Mode validation rejects clocks below 32 MHz, above 330 MHz, or above 165 MHz without a slave. Mode set initializes master and optional slave registers for input edge, width, dual-edge, deskew, sync, filter, and dual-link skew, then powers on. DPMS powers the master for active modes and powers the slave only when active pixel clock requires dual-link. Detect reads hotplug status from `SIL164_DETECT`.

## State and Persistence Behavior
`struct sil164_priv` stores the input configuration, optional slave client, and saved master/slave register snapshots for registers `0x8` through `0xe`. Hardware state persists in the transmitter registers; save/restore preserves them across display lifecycle events.

## Dependencies and Integration Points
The file integrates with `nouveau_i2c_encoder.c`, DCB-provided SIL164 platform data, Linux I2C client creation, DRM mode validation, and external TMDS paths created by NV04 DFP code.

## Risks
Dual-link slave detection treats a successful zero-length transfer as presence and can create a second client that must be unregistered exactly once. Detect depends on transmitter hotplug bits rather than EDID. Some register values are fixed policy choices, so unusual board wiring may need platform data. I2C errors return zero for reads and can cause false probe failures or stale state.

## Test Signals
Signals include module probe on SIL164 boards, single-link and dual-link clock validation, slave detection at address `0x39`, DPMS on/off for both clients, hotplug detect, save/restore across suspend, and mode programming with different input edge/width/skew platform parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/i2c/sil164_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c

## Purpose
This file provides the common bridge between Nouveau DRM encoders and slave encoder chips exposed as Linux I2C drivers.

## Important APIs, Types, and Functions
`nouveau_i2c_encoder_init` creates and binds an I2C client, holds the module owner, initializes Nouveau encoder callbacks, and applies optional platform config. Wrapper callbacks are `nouveau_i2c_encoder_mode_fixup`, `nouveau_i2c_encoder_detect`, `nouveau_i2c_encoder_save`, and `nouveau_i2c_encoder_restore`.

## Control Flow
Initialization requests the module by I2C type name, creates a client on the given adapter, verifies a driver bound, takes a module reference, records the client in `nouveau_i2c_encoder`, converts the I2C driver to a `nouveau_i2c_encoder_driver`, runs its `encoder_init`, and applies platform data through `set_config`. Failure unwinds the module ref and I2C device. Wrapper functions delegate to the slave callback table, defaulting mode fixup to true if absent.

## State and Persistence Behavior
The function installs `encoder->i2c_client`, `encoder_i2c_funcs`, and driver-private state allocated by the slave init. Module references persist while the encoder is alive; slave destroy callbacks are expected to unregister clients and release resources through `nouveau_i2c_encoder_destroy`.

## Dependencies and Integration Points
It depends on Linux I2C module autoloading, Nouveau's `encoder_i2c` abstraction, CH7006/SIL164-style drivers, and DRM encoder helper callbacks used by TV/DFP creation paths.

## Risks
Lifecycle correctness depends on slave `destroy` implementations releasing the module/device via the common destroy helper. `i2c_new_client_device` failures or unbound clients must be handled carefully. Wrappers assume callback pointers such as detect/save/restore are valid, so every slave driver must provide them when routed through helper tables.

## Test Signals
Test CH7006 and SIL164 module autoload, probe failure unwind, platform-data application, save/restore delegation, detect delegation, optional mode-fixup absence, and module unload with active/unbound encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nouveau_i2c_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h

## Purpose
This header is the pre-NV50 display and graphics register map used by NV04 display helpers, encoders, TV, and overlay code.

## Important APIs, Types, and Functions
It defines MMIO block offsets/sizes, core register addresses, VGA sequencer/graphics/CRTC/attribute indices, RAMDAC PLL/FP/TV/TMDS registers, PTV TV encoder registers, PVIDEO overlay registers, PGRAPH registers, and numerous bitfield constants used by `MASK`, `XLATE`, `NVVAL`, and direct register writes.

## Control Flow
There is no executable control flow. The constants drive all MMIO and indexed register access in `hw.c`, `hw.h`, `overlay.c`, `tvnv04.c`, `tvnv17.c`, CRTC, DAC, and DFP files.

## State and Persistence Behavior
No software state is stored. The header names hardware state that is read into `nv04_mode_state`, programmed during modesets, or manipulated live by overlay/TV helpers.

## Dependencies and Integration Points
It is included by `hw.h` and display files that need raw register addresses. Values align Nouveau code with historical XFree86/VIDIX/Haiku register knowledge and NVIF MMIO access.

## Risks
Incorrect constants can cause writes to wrong MMIO locations and hardware hangs. Some names are inferred or duplicated, and several bitfields use `high:low` macro syntax that only works with Nouveau helper macros. Shared offsets such as NV04 PVIDEO versus NV10 PVIDEO require chipset-aware callers.

## Test Signals
Build coverage plus hardware smoke tests for modeset, palette, cursor, overlay, TV, flat-panel scaling, PLL programming, and suspend/resume provide validation. Static checks for duplicate or changed constants are also useful when syncing with upstream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c

## Purpose
This file implements legacy overlay planes for NV04 and NV10-NV40 hardware, exposing YUV overlay formats and color-control properties through DRM planes.

## Important APIs, Types, and Functions
It defines `struct nouveau_plane`, supported formats `YUYV`, `UYVY`, `NV12`, and `NV21`, plane callbacks for NV10 (`nv10_update_plane`, `nv10_disable_plane`) and NV04 (`nv04_update_plane`, `nv04_disable_plane`), property handling through `nv_set_property`, and the public `nouveau_overlay_init`.

## Control Flow
Overlay init selects NV04 or NV10 implementation by chipset, allocates a plane, registers a universal overlay plane with CRTC masks and supported formats, creates range properties, attaches defaults, initializes color controls, and force-disables the plane. Update paths convert 16.16 source coordinates to integer pixels, validate scaling limits and offsets, pin the framebuffer BO into VRAM, program PVIDEO registers for source, destination, scaling, format, color key, color encoding, and luminance/chrominance controls, flip buffer selection where supported, and unpin the previously active BO. Disable stops the overlay and unpins the current BO.

## State and Persistence Behavior
Per-plane state stores current BO, buffer flip bit, color key, contrast, brightness, hue, saturation, color encoding, and DRM property objects. The active overlay BO remains pinned while displayed and is released on update/disable/destroy.

## Dependencies and Integration Points
It depends on DRM plane APIs, Nouveau GEM/BO pinning, NVIF MMIO writes, CRTC index state, `nvreg.h` PVIDEO registers, and the display constructor in `disp.c`.

## Risks
Scaling validation is hardware-specific and rejects offsets for NV04. NV04 step-size math divides by `crtc_w - 1` and `crtc_h - 1`, so degenerate sizes must be filtered by DRM callers. Pin failures abort updates. Programming lacks explicit vblank synchronization in the NV10 path. Property updates modify live registers and must match the currently programmed buffer index.

## Test Signals
Signals include plane creation on NV04 and NV10/NV30/NV40, format coverage for packed and planar YUV where supported, scaling rejection, color key enable/disable, brightness/contrast/hue/saturation changes, BT.601/BT.709 switching, repeated updates with BO pin accounting, disable/destroy cleanup, and suspend/resume with overlays active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c

## Purpose
This file provides on-chip NV17/NV4x TV norm tables, low-definition and component/HD timing data, filter coefficient generation, TV state save/load helpers, mode lists, and property/rescaler update routines.

## Important APIs, Types, and Functions
It exports `nv17_tv_norm_names`, `nv17_tv_norms`, `nv17_tv_modes`, `nv17_tv_state_save`, `nv17_tv_state_load`, `nv17_tv_update_properties`, `nv17_tv_update_rescaler`, and `nv17_ctv_update_rescaler`. Internal helpers save/load filter blocks and compute filter coefficients from overscan, flicker, and scaling ratios.

## Control Flow
Static norm tables provide either TV encoder byte arrays for PAL/NTSC-like modes or CTV PRAMDAC register arrays for HD/component modes. Save/load walks TV encoder indexed registers, horizontal/vertical filter tables, and selected PTV registers. Property update chooses PTV routing and TV encoder register values based on subconnector and pin mask, then live-loads saturation and hue fields. Rescaler update computes overscan and filter coefficients for low-definition modes, while CTV update adjusts FP valid ranges and scaling ratios in PRAMDAC registers.

## State and Persistence Behavior
The file reads and writes `struct nv17_tv_state`, including TV encoder bytes, hfilter/hfilter2/vfilter matrices, and PTV register shadows. It also mutates `nv04_display.mode_reg.crtc_reg[head]` for CTV scaling and FP timing state. Hardware state persists in PTV, TV encoder, and RAMDAC register blocks.

## Dependencies and Integration Points
It integrates with `tvnv17.c` encoder lifecycle, `tvnv17.h` structures and access macros, `hw.h` RAMDAC helpers, Nouveau CRTC indices, DRM display modes, and legacy TV connector properties.

## Risks
Much of the filter and CTV programming is empirical. Fixed-point filter math is complex and could overflow or produce invalid coefficients if property ranges change. Low-definition and component paths use different hardware blocks, so applying the wrong property path can write irrelevant registers. The state load pokes register `0x3e` to make settings latch, which is undocumented.

## Test Signals
Visual output validation across PAL, PAL-M/N/Nc, NTSC-M/J, 480i/p, 576i/p, 720p, and 1080i is important. Exercise overscan, flicker, saturation, hue, subconnector changes, save/restore, low-definition mode clocks, and component scaling on both interlaced and progressive output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c

## Purpose
This file implements support for NV04-era external TV encoders, currently probing and binding CH7006 devices over I2C and bridging them into the Nouveau DRM encoder helper model.

## Important APIs, Types, and Functions
`nv04_tv_identify` probes the configured I2C bus for supported TV encoder board info. `nv04_tv_create` constructs the DRM encoder. Helper callbacks include `nv04_tv_dpms`, `nv04_tv_prepare`, `nv04_tv_mode_set`, `nv04_tv_commit`, and `nv04_tv_destroy`. The file also defines the CH7006 board-info/platform-data table.

## Control Flow
Creation probes the DCB I2C bus, allocates a `nouveau_encoder`, initializes a TVDAC DRM encoder, records DCB output and OR, initializes the slave encoder through `nouveau_i2c_encoder_init`, creates slave resources, and attaches to the connector. Prepare powers the slave off, disables flat-panel output on the target head, unbinds the other head on dual-head chips, and binds TV routing. Mode set writes TV totals/skews/delays into the NV04 mode shadow and delegates chip-specific mode programming. DPMS updates PLL source selection bits, inhibits hsync when on, writes PRAMDAC PLL select, and delegates DPMS to the slave.

## State and Persistence Behavior
It mutates `nv04_display.mode_reg` fields such as `pllsel`, per-head CRTC `CRE_49`, `tv_setup`, and TV timing registers. The external encoder state is owned by the slave driver, while this bridge owns DRM encoder lifetime and DCB association.

## Dependencies and Integration Points
The file depends on CH7006 public parameters, Nouveau I2C encoder wrappers, DCB output entries, I2C bus probing, NV04 DFP disable/bind helpers, RAMDAC/VGA register helpers, and DRM encoder helper callbacks.

## Risks
Only probed external encoders in the static table are supported. TV PLL selection clears both CRTC TV masks before setting the active one, so multi-output assumptions are narrow. Bind/unbind sequencing touches LCD and TV setup registers and may conflict with simultaneous FP outputs. Failure after encoder init must clean both DRM and slave resources correctly.

## Test Signals
Test external CH7006 probe through DCB I2C index, TV connector resource properties, DPMS on/off PLL bits, mode set for supported timings, dual-head bind/unbind behavior, coexistence with DFP outputs, encoder destroy/unload, and connector detect delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c

## Purpose
This file implements on-chip NV17/NV4x TV output encoders, including load detection, TV mode enumeration/validation, DPMS, modeset preparation, low-definition TV programming, component/HD CTV programming, property handling, and encoder creation.

## Important APIs, Types, and Functions
The public constructor is `nv17_tv_create`. Important helpers include `nv42_tv_sample_load`, `nv17_tv_detect`, low/HD mode list functions, `nv17_tv_mode_valid`, `nv17_tv_mode_fixup`, `nv17_tv_dpms`, `nv17_tv_prepare`, `nv17_tv_mode_set`, `nv17_tv_commit`, `nv17_tv_save`, `nv17_tv_restore`, `nv17_tv_create_resources`, and `nv17_tv_set_property`.

## Control Flow
Detection first rejects use when the DAC is busy, applies board quirk pin masks where present, samples load through NV42-specific or DAC sampling logic, maps pin masks to composite, S-video, component, or SCART subconnectors, and updates DRM properties. Mode enumeration chooses low-definition TV modes or CTV-derived HD modes based on the selected norm. Mode validation enforces clock, geometry, interlace, and doublescan constraints. Prepare powers off, disables FP, moves unused FP encoders away if CTV needs FP resources, updates LCD routing, and programs DACCLK routing. Mode set fills either PTV/TV encoder state for low-definition output or CTV/FP timing state for component modes. Commit updates rescaler/properties, loads TV state, sets test-control values, and powers on.

## State and Persistence Behavior
`struct nv17_tv_encoder` stores TV state snapshots, overscan, flicker, saturation, hue, selected norm/subconnector, and pin mask. The encoder also persists saved DACCLK and PTV/TV registers. Modesets update `nv04_display.mode_reg` PRAMDAC/FP/CTV fields and live hardware registers.

## Dependencies and Integration Points
The file integrates with DRM TV properties, DCB TV configuration, board quirks, GPIO TVDAC controls, DAC load detection helpers, DFP routing helpers, `tvmodesnv17.c` tables/calculations, NV04 RAMDAC/VGA helpers, and Nouveau connector/encoder state.

## Risks
Load detection relies on analog electrical sampling and board quirks; false results affect connector status and subconnector choice. CTV mode setup steals FP resources and can disturb inactive DFP encoders. Property updates for low-definition-only controls are rejected for CTV modes, but callers must handle failures. Several register values are empirical and chipset-specific. Mode changes for norm updates require connector DPMS off.

## Test Signals
Signals include load detection on composite/S-video/component/SCART, quirked pin masks, PAL/NTSC/HD norm switching, low-definition and CTV mode enumeration, DPMS GPIO and DACCLK behavior, FP coexistence on dual-head boards, overscan/flicker/saturation/hue updates, save/restore across suspend, and reject paths for invalid modes/properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h

## Purpose
This header defines the shared on-chip NV17/NV4x TV encoder data structures, norm table contract, helper prototypes, interpolation helper, and PTV/TV-encoder register access macros.

## Important APIs, Types, and Functions
Key types are `struct nv17_tv_state`, `enum nv17_tv_norm`, `struct nv17_tv_encoder`, and `struct nv17_tv_norm_params`. It declares norm names, norm parameter table, mode table, state save/load, property/rescaler update functions, and inline `nv_write_ptv`, `nv_read_ptv`, `nv_write_tv_enc`, and `nv_read_tv_enc` helpers.

## Control Flow
Inline accessors write PTV registers directly through NVIF MMIO and access TV encoder indexed registers by writing `NV_PTV_TV_INDEX` then reading or writing `NV_PTV_TV_DATA`. The `get_tv_norm` macro derives the active norm parameters from encoder state.

## State and Persistence Behavior
`nv17_tv_state` persists TV encoder bytes, horizontal/vertical filter coefficient matrices, and selected PTV registers. `nv17_tv_encoder` embeds `nouveau_encoder` and stores current/saved TV state plus user-visible TV properties and pin-detection state.

## Dependencies and Integration Points
It depends on Nouveau encoder structures, DRM display modes, NVIF device access, and register constants from `nvreg.h` through users. `tvnv17.c` and `tvmodesnv17.c` share this header as their internal ABI.

## Risks
The state structures encode fixed register counts (`0x40`, 38 CTV registers, fixed filter dimensions); hardware additions need synchronized updates in save/load and tables. Macro-based register access has no bounds checks. Enum order is part of DRM property values and norm table indexing.

## Test Signals
Build coverage, norm property ordering checks, save/load of all tracked registers, PTV indexed access, and low-definition/HD path table indexing validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvnv17.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild

## Purpose
This build fragment lists the NV50-and-newer Nouveau display implementation objects and their debugfs-conditional CRC components.

## Important APIs, Types, and Functions
It adds display core, LUT, core channel classes, CRC, DAC/PIOR/SOR output classes, head classes, WIMM/window/base/cursor/overlay/OIMM objects, and generation-specific class files to `nouveau-y` or `nouveau-$(CONFIG_DEBUG_FS)`.

## Control Flow
There is no runtime flow. Kbuild composes the driver objects according to unconditional Nouveau display support and debugfs configuration.

## State and Persistence Behavior
No runtime state is stored. The file determines which class implementations are linked for runtime class selection by `nvif_mclass`.

## Dependencies and Integration Points
It integrates with the parent Nouveau build and class-selection code in `core.c`, `base.c`, and related display modules.

## Risks
Missing an object breaks class selection or unresolved symbols for generation-specific function tables. Debugfs CRC objects must stay conditional with CRC references guarded by `CONFIG_DEBUG_FS`.

## Test Signals
Build with debugfs enabled and disabled, across module and built-in configs. Runtime class selection on NV50 through modern GPUs validates that all required class files are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h

## Purpose
This header defines the NV50 display atomic state extensions for global display state, per-head state, and per-window/plane state.

## Important APIs, Types, and Functions
Key structures are `struct nv50_atom`, `struct nv50_head_atom`, and `struct nv50_wndw_atom`. Helper macros/functions include `nv50_atom`, `nv50_head_atom`, `nv50_head_atom_get`, `nv50_head_atom_get_new`, `nv50_head_atom_get_encoder`, and `nv50_wndw_atom`. The state carries masks for set/clear operations, mode timings, LUTs, framebuffer image layout, cursor state, base/overlay metadata, dither/procamp/output state, MST bandwidth, CRC state, notifier/semaphore, CSC, scaling, point, and blending.

## Control Flow
The header has no executable flow except inline atomic-state retrieval helpers. Those helpers fetch CRTC state from a DRM atomic transaction, cast to Nouveau private state, and return either an error pointer, new state, or the single encoder referenced by an encoder mask.

## State and Persistence Behavior
These structures are transient DRM atomic transaction state but encode hardware programming decisions that later become persistent display channel state. Mask unions (`set`/`clr`) drive which head/window blocks are emitted during commit.

## Dependencies and Integration Points
It depends on DRM atomic core, Nouveau encoder declarations, and CRC state. NV50 head, window, base, cursor, overlay, core, and output class files consume these structures during atomic check and commit.

## Risks
Bitfield widths mirror hardware method fields; overflow or truncation can silently corrupt programming. The assumption of a single encoder in `nv50_head_atom_get_encoder` must match routing logic. Mask updates must be consistent or commits may skip needed hardware changes or clear live state.

## Test Signals
Atomic modeset/plane/cursor/LUT/CSC/CRC tests, MST bandwidth commits, format/layout coverage, state duplication/reset, and debug assertions around mask transitions are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/atom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c

## Purpose
This file selects and creates the per-head NV50 base display channel, which backs primary planes on pre-window-display hardware generations.

## Important APIs, Types, and Functions
`nv50_base_new` is the public factory. It contains a class table mapping supported display base DMA channel classes to `base507c_new`, `base827c_new`, `base907c_new`, or `base917c_new`.

## Control Flow
The factory asks `nvif_mclass` to select the best supported class from the display object. If no class matches, it logs an error and returns the negative code. Otherwise, it dispatches to the selected generation constructor with the DRM device, head index, object class, and output window pointer.

## State and Persistence Behavior
This file does not store state itself. The selected constructor allocates and initializes `struct nv50_wndw` and its DMA channel.

## Dependencies and Integration Points
It depends on `nv50_disp(drm->dev)->disp->object`, NVIF class matching, and generation-specific base constructors declared in `base.h`.

## Risks
Class ordering determines preference; a wrong order can choose an older implementation on newer hardware. Unsupported classes fail primary plane creation. Constructor function-table compatibility must match the chosen class.

## Test Signals
Runtime initialization on NV50, G82/GT200/GT214, GF110, GK104/GK110, and newer supported GPUs; forced class-match failure; and primary plane creation per head are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h

## Purpose
This header declares NV50 base channel constructors and shared base-plane helper functions.

## Important APIs, Types, and Functions
It declares `base507c_new`, `base507c_new_`, `base507c_format`, base acquire/release, semaphore and LUT helpers, generation constructors `base827c_new`, `base907c_new`, `base917c_new`, exported function table `base907c`, and public factory `nv50_base_new`.

## Control Flow
There is no standalone flow. The declarations let newer class files reuse the NV507C constructor and helper methods while substituting class-specific image/LUT/CSC emitters and format lists.

## State and Persistence Behavior
No state is stored in the header. The declared functions operate on `struct nv50_wndw`, `struct nv50_wndw_atom`, and `struct nv50_head_atom` atomic/display state.

## Dependencies and Integration Points
It includes `wndw.h` and is consumed by `base.c` and all generation-specific base channel files.

## Risks
Function signatures must stay synchronized with `struct nv50_wndw_func` expectations. Exporting `base907c` for reuse by `base917c` couples newer formats to GF110-era methods.

## Test Signals
Build coverage across all base class files and runtime primary-plane programming on each supported display class validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c

## Purpose
This file implements the NV507C base channel methods and shared helper logic reused by later base channel classes.

## Important APIs, Types, and Functions
Important functions include `base507c_update`, image set/clear, LUT set/clear, notifier reset/set/clear/wait, semaphore set/clear, `base507c_acquire`, `base507c_release`, `base507c_new_`, and `base507c_new`. It exports `base507c_format` and defines the `base507c` `nv50_wndw_func` table.

## Control Flow
Acquire validates primary plane state with no scaling, updates head base metadata from framebuffer format and source coordinates, and marks color management changed when 8bpp behavior crosses LUT ownership rules. Image set emits present control, DMA ISO context, FP16 processing conversion, offset, size, storage, and format methods. Update emits the core interlock and kicks the push buffer. Constructor creates a DRM primary window, then allocates a display DMA channel with notifier/semaphore offsets and interlock data.

## State and Persistence Behavior
The functions mutate atomic head base fields, window notifier/semaphore handles, DMA push channel state, and hardware base channel methods. The active image, context DMA, LUT mode, notifier, and semaphore settings persist in the display channel until changed or cleared.

## Dependencies and Integration Points
It depends on NVIF push macros, class `cl507c`, `nv50_wndw_new_`, `nv50_dmac_create`, BO notifier access macros, DRM framebuffer formats, and `nv50_disp` sync BO layout.

## Risks
Offsets are shifted by hardware-specific granularity (`>> 8`), so alignment is critical. Storage pitch/block fields share method encoding and must match layout. Notifier waits have a 2-second timeout. FP16 processing special-case must match class format IDs. Constructor error paths leave partial `nv50_wndw` allocation to outer cleanup.

## Test Signals
Primary plane commits for every listed format, pitch and block-linear layouts, notifier/semaphore synchronization, page flips with interlock, LUT ownership changes for C8, FP16 framebuffer display, and channel allocation failure injection are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base507c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c

## Purpose
This file adapts the base channel image programming for NV827C-class display hardware while reusing most NV507C base-plane behavior.

## Important APIs, Types, and Functions
It defines `base827c_image_set`, the `base827c` `nv50_wndw_func` table, and `base827c_new`.

## Control Flow
Image set emits NV827C methods for present control, context DMA ISO array, optional FP16 gain/offset processing, surface offsets, size, storage, and params. The function table reuses NV507C acquire/release, notifier, semaphore, LUT, image clear, and update helpers. Constructor delegates to `base507c_new_` with NV507C formats and NV827C image methods.

## State and Persistence Behavior
It programs persistent base channel image state in NV827C hardware and otherwise shares state behavior with `base507c.c`.

## Dependencies and Integration Points
It depends on `cl827c` method definitions, NVIF push helpers, and the common base helper ABI in `base.h`.

## Risks
NV827C context DMA and surface method layout differs from NV507C; using the wrong function table would corrupt channel methods. The same format table is assumed valid for the class. Pitch/block encoding must be class-compatible.

## Test Signals
Primary plane display on G82/GT200/GT214 classes, FP16 processing path, pitch and block layouts, notifier/semaphore behavior inherited from NV507C, and class selection through `nv50_base_new` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base827c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c

## Purpose
This file implements GF110-era base channel image programming plus input LUT and color-space-conversion support for base planes.

## Important APIs, Types, and Functions
It defines `base907c_image_set`, LUT set/clear, `base907c_ilut`, `base907c_csc`, CSC set/clear, exported function table `base907c`, and `base907c_new`.

## Control Flow
Image set emits NV907C present control with timestamp disabled, context DMA, offsets, size, storage, and params. LUT set programs base LUT enable/mode/offset and routes output LUT to core LUT, while clear disables base/output LUTs and clears DMA LUT context. `base907c_ilut` selects interpolation mode by LUT size and sets the loader. CSC conversion maps DRM CTM S31.32 coefficients into 19-bit S3.16 two's-complement hardware fields, clamps out-of-range values, and stores a 3x4 matrix with zero offsets. CSC set emits ownership and matrix methods.

## State and Persistence Behavior
The file populates `nv50_wndw_atom` LUT and CSC fields during atomic check paths and programs persistent base channel LUT/CSC/image state during commit. It reuses notifier, semaphore, acquire/release, image clear, and update state from NV507C.

## Dependencies and Integration Points
It depends on `cl907c`, `head907d_olut_load`, DRM CTM format, NVIF push helpers, and shared base/window atomic state.

## Risks
Color conversion precision and clamping must match DRM expectations. LUT size assumptions choose between 257 and 1024 modes. CSC owner clear returns ownership to core; missing clear could leave stale plane CSC. Image method layout must match class-specific offsets.

## Test Signals
Atomic color-management tests for CTM and input LUT, C8 and true-color primary plane commits, LUT clear/set transitions, CSC identity and saturated coefficients, GF110 primary display, and class selection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base907c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c

## Purpose
This file provides the GK104/GK110 base channel constructor with an expanded supported primary-plane format list while reusing the NV907C method implementation.

## Important APIs, Types, and Functions
It defines `base917c_format` and `base917c_new`.

## Control Flow
The constructor delegates to `base507c_new_` with the exported `base907c` function table, the GK-era format list, and the class-specific interlock bit layout.

## State and Persistence Behavior
No separate state is introduced. Base channel state is managed by the reused `base907c` methods and common window/channel objects.

## Dependencies and Integration Points
It depends on `base907c`, DRM format constants, and `base507c_new_`. `base.c` selects this constructor for GK104/GK110 and newer pre-GV100 base-channel classes listed there.

## Risks
New formats such as XRGB/ARGB2101010 are exposed only if the reused NV907C method encodings support them. Any class difference not covered by the shared function table would surface as incorrect display programming.

## Test Signals
Primary plane commits for every listed format on GK-class hardware, especially RGB/BGR 10-bit and FP16 formats, plus LUT/CSC behavior inherited from NV907C are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c

## Purpose
This file selects, creates, and destroys the NV50 display core DMA channel implementation for the detected display hardware class.

## Important APIs, Types, and Functions
Public functions are `nv50_core_new` and `nv50_core_del`. The class table maps NV50 through Blackwell-era core channel classes to constructors such as `core507d_new`, `core827d_new`, `core907d_new`, `core917d_new`, `corec37d_new`, `corec57d_new`, and `coreca7d_new`.

## Control Flow
`nv50_core_new` asks `nvif_mclass` to choose the first supported class from the ordered table and dispatches to the matching constructor. If no class is supported, it logs and returns the error. `nv50_core_del` destroys the DMA channel, frees the core object, and nulls the caller pointer.

## State and Persistence Behavior
The file owns no long-term state beyond creating/freeing `struct nv50_core`; constructors initialize the function table, display pointer, and channel. Deletion tears down channel state through `nv50_dmac_destroy`.

## Dependencies and Integration Points
It depends on `nv50_disp(drm->dev)->disp->object`, NVIF class matching, and constructor declarations in `core.h`. The selected core function table drives heads, outputs, CRC, caps, window ownership, and update behavior.

## Risks
Class-table order controls preferred implementation. Missing or wrong class mappings can prevent display init on whole GPU generations. Teardown assumes the core pointer is either fully initialized enough for `nv50_dmac_destroy` or NULL.

## Test Signals
Display init across supported GPU generations, forced unsupported-class failure, suspend/unload teardown, and core channel update/caps initialization after selection validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h

## Purpose
This header defines the NV50 display core channel object, its generation-specific function table, and constructor/helper declarations for all supported core channel classes.

## Important APIs, Types, and Functions
`struct nv50_core` stores the function table, display pointer, DMA channel, and `assign_windows` flag. `struct nv50_core_func` declares hooks for init, notifier init/wait, caps init, update, window ownership, head/output function tables, and optional CRC support. The header declares core constructors, shared NV507D helpers, capability initializers, update functions, window owner helper, and output function tables for DAC/PIOR/SOR variants.

## Control Flow
There is no standalone flow. Runtime code selects a `nv50_core_func` and then calls its hooks during display init, atomic commits, capability setup, notifier synchronization, and output control.

## State and Persistence Behavior
The header describes persistent per-display core state. `assign_windows` marks whether modern core init should assign window ownership. Function tables encode generation behavior and indirectly control hardware state persistence through channel methods.

## Dependencies and Integration Points
It includes `disp.h`, `atom.h`, `crc.h`, and `nouveau_encoder.h`, and ties together head, output, CRC, and core channel implementation files.

## Risks
Function table fields are generation-specific; missing hooks cause runtime NULL dereferences or skipped hardware programming. CRC pointers are conditional on debugfs and must match build configuration. Shared helper declarations must match class-specific method layouts.

## Test Signals
Build with debugfs on/off, core init and update on all class families, notifier wait paths, caps initialization, window ownership on GV100+, and output control through DAC/SOR/PIOR validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c

## Purpose
This file implements the NV507D display core channel and shared core helpers for notifier setup, capability reads, updates, initialization, and construction.

## Important APIs, Types, and Functions
It defines `core507d_update`, `core507d_ntfy_wait_done`, `core507d_ntfy_init`, `core507d_read_caps`, `core507d_caps_init`, `core507d_init`, `core507d_new_`, and `core507d_new`, plus the `core507d` function table.

## Control Flow
Update optionally enables a write notifier, emits an UPDATE method with base and overlay interlock flags plus interrupt/driver-friendly bits, disables notify, and kicks the push buffer. Capability init clears the caps notifier, sends `GET_CAPABILITIES`, then waits up to two seconds for the notifier done bit. Init sets the context DMA notifier. Constructor allocates `struct nv50_core`, assigns the function table/display pointer, and creates the display DMA channel using the shared sync BO.

## State and Persistence Behavior
The file initializes notifier memory in the sync BO, programs persistent core channel context DMA, and uses push-buffer methods to update hardware state. The function table references head/output implementations for NV507D-era hardware.

## Dependencies and Integration Points
It depends on NVIF push/timer, class `cl507d`, BO notifier macros, `nv50_dmac_create`, `nv50_disp` sync layout, and head/output function tables `head507d`, `dac507d`, `sor507d`, and `pior507d`.

## Risks
Notifier and caps waits can time out, but caps init returns success after logging timeout. Update interlock flags must match pending plane/core changes or commits can tear. Constructor error paths can leave allocated core memory for caller cleanup.

## Test Signals
Core channel allocation, init notifier DMA, atomic commits with and without notify, caps reads, notifier timeout injection, output control on DAC/SOR/PIOR, and suspend/unload channel destruction are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core507d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c

## Purpose
This file defines the GT200/G82-era core channel function table, reusing NV507D core mechanics with a generation-specific head implementation.

## Important APIs, Types, and Functions
It defines the static `core827d` `nv50_core_func` table and public constructor `core827d_new`.

## Control Flow
The constructor delegates to `core507d_new_` with the `core827d` function table. The function table reuses NV507D init, notifier, caps, and update helpers, selects `head827d`, and keeps NV507D DAC/SOR/PIOR output handlers.

## State and Persistence Behavior
No unique state is introduced; persistent core channel and notifier behavior are inherited from NV507D helpers.

## Dependencies and Integration Points
It depends on `head827d`, `core507d_new_`, and shared output function tables. `core.c` selects it for G82, GT200, GT206, and GT214 classes.

## Risks
The file assumes core method layout remains compatible with NV507D while head programming differs. If output methods diverged for a selected class, reused function tables would misprogram hardware.

## Test Signals
Core channel init and atomic commits on G82/GT200/GT214, head-specific modesets through `head827d`, output control, and caps notifier behavior inherited from NV507D are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c

## Purpose
This file defines the GF110-era core channel function table and a class-specific capability notifier initialization path.

## Important APIs, Types, and Functions
It implements `core907d_caps_init`, defines the `core907d` function table, and provides `core907d_new`.

## Control Flow
Capability init clears the GF110 notifier field (`NV907D_CORE_NOTIFIER_3.CAPABILITIES_4.DONE`), reuses `core507d_read_caps`, then waits for the GF110 notifier done bit. The constructor delegates to `core507d_new_`. The function table reuses NV507D init/notifier/update, selects `head907d`, enables optional `crc907d`, and uses `dac907d`/`sor907d` output handlers.

## State and Persistence Behavior
State behavior follows the shared core channel, but capability completion is tracked in a different notifier layout. Optional CRC state is available under debugfs.

## Dependencies and Integration Points
It depends on `cl907d`, BO notifier macros, NVIF timer, `head907d`, `crc907d`, `dac907d`, and `sor907d`.

## Risks
Caps init logs timeout but returns success. Reusing `core507d_read_caps` assumes the GET_CAPABILITIES method is compatible while notifier layout differs. CRC pointers are build-conditional.

## Test Signals
GF110 core init, caps read completion, timeout injection, CRC debugfs capture where enabled, DAC/SOR output control, and atomic commit update behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c

## Purpose
This file defines the GK/GM/GP-era core channel function table by combining GF110 capability handling with newer head programming.

## Important APIs, Types, and Functions
It defines the `core917d` `nv50_core_func` table and public `core917d_new`.

## Control Flow
The constructor delegates to `core507d_new_`. The function table reuses NV507D init/notifier/update, GF110 `core907d_caps_init`, selects `head917d`, enables optional `crc907d`, and uses `dac907d`/`sor907d` output handlers.

## State and Persistence Behavior
No unique state is introduced; channel, notifier, caps, and output state use shared helpers and selected function tables.

## Dependencies and Integration Points
It depends on `head917d`, shared `core507d` helpers, `core907d_caps_init`, optional CRC, and GF110-era output handlers. `core.c` selects it for GK104/GK110, GM107/GM200, GP100/GP102, and related classes.

## Risks
The class compatibility assumption spans several GPU generations. Any method or notifier divergence not represented by this table could break caps, update, or output control. CRC support is reused from GF110.

## Test Signals
Core init and modeset on Kepler, Maxwell, and Pascal, caps reads, CRC debugfs where enabled, SOR/DAC output control, and suspend/resume are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c

## Purpose
This file implements the GV100-era core channel behavior for modern window-based display hardware, including window ownership, modern update interlocks, notifier handling, mapped capabilities, and initialization of window usage bounds.

## Important APIs, Types, and Functions
It defines `corec37d_wndw_owner`, `corec37d_update`, `corec37d_ntfy_wait_done`, `corec37d_ntfy_init`, `corec37d_caps_init`, `corec37d_init`, the `corec37d` function table, and `corec37d_new`.

## Control Flow
Init sets the context DMA notifier and programs usage/format bounds for eight windows, then marks `assign_windows` true. Window owner emits ownership for each window, assigning pairs to heads by `i >> 1`. Update optionally enables a notifier, emits cursor and window interlock flags, emits the modern UPDATE method, optionally disables notify, and kicks. Caps init constructs and maps a `GV100_DISP_CAPS` object instead of reading caps through the legacy notifier path. Notifier init/reset writes the modern notifier status and payload fields.

## State and Persistence Behavior
The file persists core channel context DMA, window usage bounds, window ownership, caps object mapping, notifier memory, and the `assign_windows` flag. Update methods synchronize cursor/window interlocks rather than legacy base/overlay interlocks.

## Dependencies and Integration Points
It depends on class `clc37d`, pushc37b macros, NVIF object construction/mapping, `headc37d`, `sorc37d`, optional `crcc37d`, `nv50_dmac` construction via `core507d_new_`, and modern `nv50_wndw`/cursor commit paths.

## Risks
The window count is hard-coded to eight with `XXX` comments; future or smaller hardware can diverge. Window-to-head ownership uses a fixed two-windows-per-head mapping. Caps object map failures need cleanup by higher layers. Usage bounds restrict scaling and format support; wrong values can reject valid commits or allow unsupported fetches.

## Test Signals
GV100/Turing-family init, caps object mapping, window assignment, atomic commits with cursor and window interlocks, notifier completion, multi-head plane distribution, CRC debugfs where enabled, and failure injection for caps construction/mapping validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec37d.c -->
