# Research Group subset-b-003546

Source-tree-aligned grouped research for subset B work item `subset-b-003546`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c

## Purpose

`ast_post.c` contains AST DRM driver's low-level POST helpers that route memory-mapped register access through the device's DWM window and dispatch generation-specific GPU initialization. It also exposes small memory-controller test helpers used by the AST POST implementations.

## Important APIs, Types, And Functions

- `__ast_mindwm(void __iomem *regs, u32 r)` and `__ast_moutdwm(void __iomem *regs, u32 r, u32 v)`: raw helpers that select the 64 KiB DWM aperture by writing the high address bits to `0xf004`, trigger selection through `0xf000`, poll until the selected window matches, then read or write `0x10000 + low16(r)`.
- `ast_mindwm()` and `ast_moutdwm()`: `struct ast_device` wrappers around the raw helpers.
- `ast_post_gpu(struct ast_device *ast)`: chooses `ast_2600_post`, `ast_2500_post`, `ast_2300_post`, `ast_2100_post`, or `ast_2000_post` based on `AST_GEN(ast)`.
- `mmc_test()` and `mmc_test_burst()`: issue memory controller self-test commands at DWM address `0x1e6e0070` and poll for completion/error bits.

## Control Flow

The DWM helpers first program the aperture selector, then spin until the hardware reports the selected high address bits before performing the final register access. `ast_post_gpu()` is a straight generation cascade from newest to oldest with error propagation from the selected POST function. `mmc_test()` clears the test register, starts a test from `datagen` and `test_ctl`, then polls bits `0x3000`: bit `0x2000` or timeout is failure, any completion bit without error is success, and the test control register is cleared before returning.

## State And Persistence Behavior

The file persists no software state. It mutates AST hardware registers: DWM aperture selection, generation-specific POST side effects through called functions, and memory-controller test control/status. A failed `mmc_test()` timeout explicitly clears the test register to leave the controller idle.

## Dependencies And Integration Points

It depends on `ast_drv.h` for device layout, generation detection, and register accessors, and on `ast_post.h` for prototypes. The generation-specific POST functions are implemented in sibling AST source files. The code runs during AST device bring-up before normal KMS operation.

## Risks And Edge Cases

The DWM polling loops have no timeout, so broken register-window selection can hang the caller. `mmc_test()` has a large software timeout but no sleep, so failures can burn CPU during POST. Generation routing depends entirely on correct `AST_GEN()` classification. The DWM helpers assume the caller supplies valid register-window addresses and that `ast->regs` is already mapped.

## Test Signals

Useful signals include probe/POST on AST2000/2100/2300/2500/2600-era hardware, fault injection around POST return codes, memory-controller test pass/fail paths, and boot tests where the DWM aperture is exercised before modeset initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h

## Purpose

`ast_post.h` declares AST POST support primitives and the compact DRAM timing table representation consumed by generation-specific AST initialization code. It centralizes sentinel/control entries for timing-table interpreters and exposes memory-controller test helpers.

## Important APIs, Types, And Macros

- `struct ast_dramstruct`: a `{ u16 index; u32 data; }` entry used for DRAM programming tables.
- `__AST_DRAMSTRUCT_DRAM_TYPE`: hardware-field index for DRAM type.
- `__AST_DRAMSTRUCT_UDELAY` and `__AST_DRAMSTRUCT_INVALID`: pseudo-indexes for table delays and end-of-table markers.
- `AST_DRAMSTRUCT_INIT()`, `AST_DRAMSTRUCT_UDELAY()`, `AST_DRAMSTRUCT_INVALID`, and `AST_DRAMSTRUCT_IS()`: helpers for defining and decoding DRAM table entries.
- Raw DWM access prototypes, `mmc_test()`, `mmc_test_burst()`, plus default extended-register setup prototypes for AST2000 and AST2300 families.

## Control Flow

The header has no runtime control flow. Its macros define the token stream that table walkers use: hardware-index writes, explicit microsecond delays, and invalid/end sentinels.

## State And Persistence Behavior

No state is stored here. The structures and constants describe writes that persist in AST memory-controller and VGA/extended registers when interpreted by POST code.

## Dependencies And Integration Points

It includes Linux integer limits/types and forward-declares `struct ast_device`. It integrates with AST generation-specific POST files, `ast_post.c`, and DRAM timing tables that need uniform pseudo-commands.

## Risks And Edge Cases

The pseudo-index values must not collide with real hardware indexes. `AST_DRAMSTRUCT_INVALID` stores `U32_MAX` as data, so consumers should treat the index as authoritative. Table walkers must handle delay entries and sentinels before issuing hardware writes.

## Test Signals

Compile coverage across AST POST files, table-walk tests that include write/delay/end entries, and hardware POST on each generation that uses these table structures are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_post.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h

## Purpose

`ast_reg.h` names AST VGA I/O register offsets and important bit fields used by the modesetting and output-detection code. It is a small hardware ABI header for VGA sequencer, CRTC, graphics, misc, and DisplayPort-related AST extension registers.

## Important APIs, Types, And Macros

The header exports only macros. Key groups include:

- VGA I/O aperture definitions: `AST_IO_MM_OFFSET`, `AST_IO_MM_LENGTH`, and offsets such as `AST_IO_VGAMR_*`, `AST_IO_VGASRI`, `AST_IO_VGACRI`, and `AST_IO_VGAIR1_R`.
- VGA enable/control bits: `AST_IO_VGAMR_IOSEL`, `AST_IO_VGAER_VGA_ENABLE`, `AST_IO_VGASR1_SD`, and `AST_IO_VGACR17_SYNC_ENABLE`.
- AST extended CRTC bits: password `AST_IO_VGACR80_PASSWORD`, memory-reservation/memory-size masks, VGA I/O disable and MMIO enable bits, DVO enable, cursor format/enable bits, and VRAM initialization status bits.
- Output-detection fields: `AST_IO_VGACRD1_TX_TYPE_MASK` with transmitter type values for no TX, ITE66121, SIL164, CH7003, DP501, ANX9807, embedded DP501 firmware, and ASTDP.
- DisplayPort flags for EDID validity, link success, HPD, video enable, PHY sleep, and 24-bpp mode.

## Control Flow

This file has no control flow. Consumers use the offsets with AST I/O helpers and test or update bit fields to enable VGA/MMIO access, infer display transmitter type, manage sync/video state, and query BMC/firmware status.

## State And Persistence Behavior

The macros describe hardware register state. Writes through consumers persist in AST VGA/DisplayPort control registers until later register writes, reset, or firmware/BMC action. Some fields mirror SoC or firmware state such as VRAM initialization and MCU firmware execution.

## Dependencies And Integration Points

It includes `<linux/bits.h>` for `BIT()` and `GENMASK()`. It is consumed by AST KMS, output, DDC, DP, and initialization code wherever direct VGA-style I/O registers are accessed.

## Risks And Edge Cases

Several fields are mirrors of firmware or BMC-owned state and should be treated as hardware contracts. Output transmitter type values are encoded in shifted/masked register bits, so consumers must apply the mask correctly. Sync/video control bits can blank the display if changed in the wrong sequence.

## Test Signals

Build coverage for AST, register read/write smoke tests during probe, output-type detection on boards with VGA/DVI/DP transmitters, VRAM init status handling, and DP HPD/link/EDID tests validate this header's use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c

## Purpose

`ast_sil164.c` creates the DRM encoder and connector for AST boards with a Silicon Image SIL164 TMDS/DVI transmitter. It mirrors the AST VGA connector behavior while using a DVI-I connector type and a TMDS encoder.

## Important APIs, Types, And Functions

- `ast_sil164_output_init(struct ast_device *ast)`: creates an AST DDC adapter, initializes `ast->output.sil164.encoder`, initializes the DVI-I connector with DDC, adds helper callbacks, sets polling flags, and attaches the connector to the encoder.
- `ast_sil164_connector_helper_detect_ctx()`: probes physical DDC status, updates `ast_connector->physical_status`, bumps `connector->epoch_counter` on physical changes, but always returns logical `connector_status_connected`.
- `ast_sil164_connector_helper_get_modes()`: uses EDID modes when the physical connector is connected; otherwise clears EDID and installs no-EDID fallback modes up to 4096x4096 with 1024x768 preferred.
- Static encoder/connector funcs use DRM atomic state helpers and standard cleanup.

## Control Flow

Initialization is DDC creation, encoder creation, connector creation, helper addition, property setup, physical-status initialization, and encoder attachment. Detection intentionally separates physical DDC state from logical connector state so BMC display paths remain available without a monitor. Mode enumeration follows that physical status to decide between EDID and fallback modes.

## State And Persistence Behavior

The file stores connector state in `ast_connector->physical_status` and increments the DRM connector epoch counter when physical DDC status changes. DRM core owns connector/encoder lifetime after initialization. No hardware registers are directly programmed here.

## Dependencies And Integration Points

It depends on AST DDC creation, `struct ast_device` output storage, and DRM connector/encoder helper APIs. It integrates with the AST single CRTC through `possible_crtcs = drm_crtc_mask(crtc)`.

## Risks And Edge Cases

Always reporting connected is intentional for server/BMC usability but can surprise generic hotplug assumptions. If `drm_encoder_init()` succeeds and connector init later fails, cleanup relies on higher-level resource management; this local function simply returns the error. Fallback mode generation must remain compatible with AST hardware limits enforced elsewhere.

## Test Signals

Test with SIL164 hardware connected and disconnected, verify EDID modes when DDC succeeds, verify 1024x768 preferred fallback without EDID, monitor connector epoch changes across plug/unplug, and run DRM atomic modeset and hotplug tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_sil164.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h

## Purpose

`ast_tables.h` contains legacy VGA standard-mode programming tables ported from the xf86-video-ast driver. These tables define sequencer, CRTC, attribute, and graphics-controller register values for text, EGA, VGA, high-color, and true-color baseline modes.

## Important APIs, Types, And Macros

- Mode index macros: `TextModeIndex`, `EGAModeIndex`, `VGAModeIndex`, `HiCModeIndex`, and `TrueCModeIndex`.
- `vbios_stdtable[]`: static table of `struct ast_vbios_stdtable` entries, each with a misc output byte and arrays for sequencer, CRTC, attribute, and graphics-controller values. Register arrays use `0xff` as visible terminators in several sub-arrays.

## Control Flow

The header has no executable control flow. Modesetting code indexes the table, then writes the contained values to VGA register groups in the order expected by the AST hardware/VBIOS model.

## State And Persistence Behavior

No software state is stored. The table values become persistent VGA register state once a consumer programs them during mode setup or reset.

## Dependencies And Integration Points

It includes `ast_drv.h` for the `struct ast_vbios_stdtable` definition. It integrates with AST VGA modeset code that needs a known standard VGA register base before enhanced timing programming.

## Risks And Edge Cases

The data is a hardware programming contract; a single byte can change sync, timing, memory layout, or attribute behavior. Because it is a header with a `static const` definition, each including translation unit receives its own private copy. Consumers must not assume every sub-array has the same terminator semantics.

## Test Signals

Validation signals are successful AST mode initialization from text/VGA-style defaults, regression tests around standard modes, visual output on legacy VGA/DVI paths, and diffs against the original vendor or xf86-video-ast tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_tables.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c

## Purpose

`ast_vbios.c` implements AST's built-in VBIOS-like mode timing database and lookup logic. It maps common display resolutions and refresh rates to AST-specific timing entries and chooses the best entry for a requested DRM display mode.

## Important APIs, Types, And Functions

- Static `res_*` arrays of `struct ast_vbios_enhtable`: timing tables for 4:3, 16:9, and 16:10 modes from 640x480 through 1920x1200. Entries include totals, active area, porches, sync widths, DCLK index, flags, refresh, refresh index, and mode ID.
- Resolution table groups: `res_table_wuxga`, `res_table_fullhd`, `res_table_wsxga_p`, and base `res_table`.
- `__ast_vbios_find_mode_table()`: scans a null-terminated table group for matching `hde` and `vde`.
- `ast_vbios_find_mode_table()`: chooses which resolution groups are available based on `ast->support_wuxga`, `support_fullhd`, and `support_wsxga_p`, then falls back to the base table.
- `ast_vbios_find_mode()`: filters candidate refresh entries by sync polarity and chooses the highest table refresh rate not greater than the requested mode refresh.

## Control Flow

The public lookup starts by selecting a resolution table allowed by device capability flags. If no resolution table matches, it returns `NULL`. Otherwise it computes requested refresh through `drm_mode_vrefresh()`, iterates valid table entries until `AST_VBIOS_INVALID_MODE`, skips entries whose sync polarity conflicts with the DRM mode flags, and returns the closest non-higher refresh entry.

## State And Persistence Behavior

The file stores static read-only timing tables. It does not mutate state. The selected timing entry drives later AST register programming and therefore influences persistent display-timing state in hardware.

## Dependencies And Integration Points

It depends on `ast_drv.h`, `ast_vbios.h`, and DRM display mode fields. It integrates with AST CRTC/modeset code that translates `ast_vbios_enhtable` entries into VGA/AST register writes, and with output capability discovery that sets the `support_*` flags.

## Risks And Edge Cases

The lookup intentionally refuses refresh rates above the request, so a request slightly below a supported rate may fail to choose an otherwise usable higher refresh. Sync polarity filtering can eliminate all modes for a resolution. Capability flags gate wide/full-HD/WUXGA modes, so incorrect transmitter detection can hide modes. Table data is hardware-specific and brittle.

## Test Signals

Mode-validation and modeset tests should cover each resolution group, capability-flag combinations, sync polarity mismatches, refresh selection boundaries, and actual display output at wide/full-HD/WUXGA timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h

## Purpose

`ast_vbios.h` defines AST enhanced-mode timing flags, DCLK indexes, the `struct ast_vbios_enhtable` layout, and the mode lookup API used by AST modeset code.

## Important APIs, Types, And Macros

- Timing flags: character clock, half/double scan, border, line compare, widescreen/new-mode indicators, polarity flags, and `AST2500PreCatchCRT`.
- Sync bundles: `SyncPP`, `SyncPN`, `SyncNP`, and `SyncNN`.
- DCLK index macros from `VCLK25_175` through `VCLK118_25`; these are AST clock-table indexes, not raw frequencies.
- `struct ast_vbios_enhtable`: horizontal/vertical totals, active area, porch/sync fields, clock index, flags, refresh metadata, and AST mode ID.
- `AST_VBIOS_INVALID_MODE` and `ast_vbios_mode_is_valid()`: sentinel construction and validity test.
- `ast_vbios_find_mode()`: public lookup prototype.

## Control Flow

Only the inline validity helper has logic: a mode is valid when horizontal total, vertical total, and refresh rate are nonzero. All other macros define data consumed by `ast_vbios.c` and modeset register programming.

## State And Persistence Behavior

No mutable state exists in this header. The constants encode display timing choices that persist in hardware after consumers program a mode.

## Dependencies And Integration Points

It includes Linux types and forward-declares AST/DRM structures. It is paired with `ast_vbios.c`, AST clock programming, and CRTC modeset code that interprets the flags and DCLK indexes.

## Risks And Edge Cases

DCLK indexes are semantic indexes into another clock-programming table; treating them as frequencies would be wrong. The invalid sentinel relies on zero total/refresh fields. Polarity flags are used inversely in some mode-filtering checks, so changes must be validated against `ast_vbios_find_mode()`.

## Test Signals

Build coverage, static checks for sentinel termination of timing arrays, mode lookup unit tests if available, and display output tests for modes using every DCLK index are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vbios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c

## Purpose

`ast_vga.c` creates the DRM DAC encoder and VGA connector for AST devices. It provides BMC-friendly fallback modes when no physical monitor is detected while keeping physical DDC state for epoch changes.

## Important APIs, Types, And Functions

- `ast_vga_output_init(struct ast_device *ast)`: creates DDC, initializes a `DRM_MODE_ENCODER_DAC`, initializes the VGA connector with DDC, sets helper callbacks/polling flags, stores initial physical status, and attaches connector to encoder.
- `ast_vga_connector_helper_detect_ctx()`: reads DDC-based physical status, bumps `connector->epoch_counter` on changes, stores the physical status, and always reports logical connected.
- `ast_vga_connector_helper_get_modes()`: returns EDID modes when physically connected; otherwise clears EDID and adds fallback modes with 1024x768 preferred.
- Standard DRM atomic connector funcs and encoder cleanup.

## Control Flow

The init flow mirrors the SIL164 path: DDC, encoder, connector, helper setup, polling setup, status seed, attach. Detection separates physical status from logical availability. Mode enumeration chooses EDID or no-EDID fallback based on physical status.

## State And Persistence Behavior

`ast_connector->physical_status` and the DRM epoch counter track physical hotplug changes. The file does not directly persist hardware register state.

## Dependencies And Integration Points

It depends on `ast_ddc_create()`, AST output storage, and DRM connector/encoder helpers. It integrates with the AST CRTC through `possible_crtcs`.

## Risks And Edge Cases

Returning connected even when DDC reports disconnected is deliberate for BMC remote-console behavior but can produce modes without a monitor. Error paths return without local cleanup after partial initialization. Fallback maximum mode generation may advertise modes later rejected by hardware-specific mode validation.

## Test Signals

Validate VGA EDID and no-EDID paths, connector polling and epoch changes, fallback preferred mode, atomic modesets with connected and disconnected VGA, and cleanup during driver unload after partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/ast/ast_vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig

## Purpose

This Kconfig file exposes the Atmel HLCDC DRM display-controller driver as `DRM_ATMEL_HLCDC`.

## Important APIs, Types, And Symbols

- `config DRM_ATMEL_HLCDC`: tristate option named "DRM Support for ATMEL HLCDC Display Controller".
- Dependencies: `DRM`, `OF`, `COMMON_CLK`, and either `MFD_ATMEL_HLCDC && ARM` or `COMPILE_TEST`.
- Selects: `DRM_CLIENT_SELECTION`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, and `DRM_PANEL`.

## Control Flow

Kconfig selection controls whether the module objects in the local Makefile are built. There is no runtime control flow.

## State And Persistence Behavior

The symbol persists in kernel configuration and controls module/built-in compilation. It does not store runtime state.

## Dependencies And Integration Points

It ties the DRM display subdriver to the parent Atmel HLCDC MFD, device tree, clocks, DMA GEM helpers, KMS helpers, and panel framework.

## Risks And Edge Cases

The `COMPILE_TEST` path permits non-ARM build coverage without real MFD hardware. Missing selected helpers or parent MFD support will prevent useful runtime probing even if compilation succeeds.

## Test Signals

Kconfig build tests for built-in/module/off states, ARM device-tree probe tests with `MFD_ATMEL_HLCDC`, and `COMPILE_TEST` coverage on other architectures validate the symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile

## Purpose

The Makefile defines how the Atmel HLCDC DRM driver is built from its CRTC, device-core, output, and plane components.

## Important APIs, Types, And Targets

- `atmel-hlcdc-dc-y`: composite object list containing `atmel_hlcdc_crtc.o`, `atmel_hlcdc_dc.o`, `atmel_hlcdc_output.o`, and `atmel_hlcdc_plane.o`.
- `obj-$(CONFIG_DRM_ATMEL_HLCDC) += atmel-hlcdc-dc.o`: builds the composite object when the Kconfig symbol is enabled.

## Control Flow

There is no runtime flow. Kbuild links the listed objects into one driver object in the declared order.

## State And Persistence Behavior

The file only affects build artifacts. It does not define runtime state.

## Dependencies And Integration Points

It integrates with the local Kconfig symbol and Linux DRM/Kbuild infrastructure. All runtime pieces in the folder are compiled together as one module or built-in unit.

## Risks And Edge Cases

Omitting one object breaks unresolved symbols across CRTC/device/output/plane boundaries. Object order is generally not semantically significant here, but all four pieces are required for a functional driver.

## Test Signals

Build `CONFIG_DRM_ATMEL_HLCDC=y` and `m`, run `modpost`, and boot/probe the module to ensure all cross-file symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c

## Purpose

`atmel_hlcdc_crtc.c` implements the DRM CRTC for Atmel/Microchip HLCDC and XLCDC display controllers. It validates modes, programs global timing/output registers, controls enable/disable sequencing, handles vblank/page-flip events, and creates the CRTC around the primary/cursor planes.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_crtc_state`: extends DRM CRTC state with selected output mode and XLCDC DPI flag.
- `struct atmel_hlcdc_crtc`: wraps `drm_crtc`, links the device controller, stores pending vblank event, and CRTC id.
- `atmel_hlcdc_crtc_mode_set_nofb()`: converts adjusted DRM timing into HLCDC CFG registers, selects pixel-clock divider/source, applies bus clock polarity, and writes output mode/sync polarity/DPI bits.
- `atmel_hlcdc_crtc_atomic_check()`: selects output bus format, prepares discard area, and balances AHB routing across planes.
- `atmel_hlcdc_crtc_atomic_enable()` and `_disable()`: sequence runtime PM, pinctrl, system clock, pixel clock, sync/display enables, and XLCDC CM/SD bits with status polling.
- `atmel_hlcdc_crtc_irq()`: handles SOF vblank and completes pending page-flip events.
- `atmel_hlcdc_crtc_create()`: picks base/cursor planes from layer descriptors, allocates the CRTC, assigns overlay `possible_crtcs`, and enables gamma/color-management support.

## Control Flow

Modeset programming starts by locating the active encoder/connector to read bus flags, then writes sync, porch, display size, clock divider, polarity, and output mode registers. Atomic check first intersects or unions connector-supported output formats according to SoC constraints, then delegates plane preparation. Enable and disable use ordered register writes plus `regmap_read_poll_timeout()` to wait for clock/sync/display status transitions; XLCDC adds CM/SD sequencing. Atomic flush transfers a pending event to private state under `event_lock`, and the IRQ path sends it after vblank.

## State And Persistence Behavior

Persistent software state includes extended CRTC state fields, pending page-flip event pointer, CRTC id, and `dc->crtc`. Hardware state persists in HLCDC CFG, EN/DIS/SR, interrupt, clock, sync, display, output-mode, and XLCDC-specific registers. Runtime PM forbids suspend while enabled and allows it again on disable.

## Dependencies And Integration Points

The file depends on Linux clocks, pinctrl, runtime PM, regmap, MFD HLCDC register definitions, videomode/DRM atomic helpers, and local plane/output helpers. It integrates with connector bus formats through `atmel_hlcdc_encoder_get_bus_fmt()` and with plane state through `atmel_hlcdc_plane_prepare_disc_area()` and `atmel_hlcdc_plane_prepare_ahb_routing()`.

## Risks And Edge Cases

Clock divider selection trades higher/lower error and may clamp when the divider field overflows. `connector` may be absent, so bus flags are optional. Output format selection can fail if connectors have no common format on SoCs with conflicting formats. Poll timeouts only warn, leaving the disable/enable path to continue. Page-flip event handling assumes vblank get succeeds; `WARN_ON` catches anomalies.

## Test Signals

Mode validation for porch/sync bounds, atomic commits across RGB bus widths and DSI encoders, suspend/resume while enabled, vblank/page-flip completion, clock divider accuracy, XLCDC and legacy HLCDC enable/disable tests, and multi-plane atomic checks are important validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c

## Purpose

`atmel_hlcdc_dc.c` is the main platform DRM driver for Atmel/Microchip HLCDC/XLCDC display controllers. It describes SoC-specific layer layouts and display limits, performs DRM device load/unload, installs interrupts, initializes modesetting, and handles PM suspend/resume.

## Important APIs, Types, And Functions

- SoC descriptor tables: layer layouts and `struct atmel_hlcdc_dc_desc` instances for at91sam9n12, at91sam9x5, sama5d2/d3/d4, sam9x60, sam9x75 XLCDC, and sama7d65 XLCDC.
- `atmel_hlcdc_of_match[]`: maps parent MFD compatible strings to descriptors.
- `atmel_hlcdc_dc_mode_valid()`: validates DRM mode porch/sync/display dimensions against descriptor limits.
- IRQ helpers: `atmel_hlcdc_dc_irq_handler()`, install/uninstall/disable/postinstall, and per-layer dispatch to plane IRQ handlers.
- `atmel_hlcdc_dc_modeset_init()`: initializes mode config, planes, CRTC, and outputs, sets min/max dimensions and atomic funcs.
- `atmel_hlcdc_dc_load()` / `_unload()`: bind descriptor/MFD data, enable clocks/runtime PM, initialize vblank/modeset/IRQ, and clean up.
- Platform driver hooks: probe, remove, shutdown, suspend, resume, with `drm_module_platform_driver()`.

## Control Flow

Probe allocates the DRM device, loads it, registers it, then starts the DRM client helper. Load matches the parent MFD node, enables the peripheral clock, enables runtime PM, initializes vblank/modeset, resets mode config, installs IRQs under runtime PM, stores platform data, and starts polling. IRQ handling reads IMR and ISR, masks active status, handles SOF as CRTC vblank, then dispatches layer status bits. Suspend saves atomic state and interrupt mask, disables interrupts and the peripheral clock; resume restores the clock, interrupt mask, and atomic state.

## State And Persistence Behavior

Persistent software state lives in `struct atmel_hlcdc_dc`: descriptor pointer, MFD pointer, CRTC pointer, layer array, DMA descriptor pool, DRM device, and saved suspend state/IMR. Hardware state includes HLCDC layer/global registers, interrupt masks, and clock state. Suspend stores a DRM atomic state pointer until resume consumes it.

## Dependencies And Integration Points

It depends on the Atmel HLCDC MFD, regmap, clocks, IRQs, runtime PM, platform bus, DRM GEM DMA helpers, KMS helpers, and local plane/CRTC/output code. Device-tree compatible strings on the parent MFD select the hardware descriptor.

## Risks And Edge Cases

Descriptor accuracy is critical because register offsets, layer capabilities, maximum mode sizes, clock-source behavior, and XLCDC operations all derive from tables. The vertical sync check uses `max_spw` for `vsync_len`, matching the existing code but easy to misread against `max_vpw`. IRQ status is shared between SOF and layer bits; stale masks can cause missed or spurious handling. Suspend/resume assumes a valid `dev_private` and successful clock re-enable.

## Test Signals

Build and boot on each compatible family, probe/remove cycles, vblank IRQ tests, page flips, suspend/resume with active scanout, mode-boundary tests, plane overrun debug signals, runtime PM checks, and device-tree descriptor validation are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h

## Purpose

`atmel_hlcdc_dc.h` is the shared register, type, and cross-file API contract for the Atmel HLCDC/XLCDC DRM driver. It defines layer register offsets/bit fields, DMA descriptors, layer/plane/controller descriptors, operation tables for legacy vs XLCDC variants, and helper accessors.

## Important APIs, Types, And Macros

- Register and bit macros for common HLCDC layer control, IRQ, DMA, format, position/size, alpha/blending, discard area, scaler, CLUT, and XLCDC-specific layer registers.
- `struct atmel_hlcdc_layer_cfg_layout`: per-layer CFG register layout, with zero meaning unsupported.
- `struct atmel_hlcdc_dma_channel_dscr`: hardware DMA descriptor ordered as address, control, next, self and aligned to 64 bits.
- `enum atmel_hlcdc_layer_type`, `struct atmel_hlcdc_formats`, `struct atmel_hlcdc_layer_desc`, `struct atmel_hlcdc_layer`, `struct atmel_hlcdc_plane`, and `struct atmel_hlcdc_dc`.
- `struct atmel_lcdc_dc_ops`: legacy/XLCDC operation callbacks for scaling, buffer updates, disable/update, CSC init, and IRQ debug.
- Inline register helpers: layer register/CFG/CLUT read-write and layer initialization.
- Cross-file prototypes for mode validation, plane creation/IRQ/preparation, CRTC IRQ/create, and output creation/bus-format lookup.

## Control Flow

The header only has inline register access helpers. Runtime control flow is supplied by function pointers in `atmel_lcdc_dc_ops`, allowing descriptor-selected code to choose legacy HLCDC or XLCDC implementations at atomic update time.

## State And Persistence Behavior

The declared structures hold the driver's core persistent state: DRM device, active layer descriptors, DMA descriptor pool, CRTC pointer, MFD/regmap pointers, and suspend snapshot. Hardware state persists in layer registers and DMA descriptors that the display controller fetches.

## Dependencies And Integration Points

It depends on regmap and DRM plane types plus MFD register definitions included by C files. All local C files include this header to share SoC descriptors, layer abstractions, and operation callbacks.

## Risks And Edge Cases

The DMA descriptor field order and alignment are hardware ABI requirements. Layout fields using zero as unsupported mean register ID 0 cannot be represented as a configurable CFG slot except where handled separately. Legacy and XLCDC bits overlap semantically but not always numerically, so ops must match descriptor type. Wrong layer offsets or CLUT offsets can corrupt unrelated hardware registers.

## Test Signals

Compile all local C files, run static checks around descriptor/layout initialization, validate DMA descriptor alignment, exercise both `atmel_hlcdc_ops` and `atmel_xlcdc_ops`, and inspect register traces on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c

## Purpose

`atmel_hlcdc_output.c` discovers downstream bridges/panels from device-tree graph endpoints and creates simple DRM encoders for HLCDC RGB output paths. It also records the endpoint bus format advertised by the `bus-width` property.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_rgb_output`: wraps a DRM encoder and cached media bus format.
- `atmel_hlcdc_encoder_get_bus_fmt(struct drm_encoder *encoder)`: returns the cached bus format for CRTC output-mode selection.
- `atmel_hlcdc_of_bus_fmt()`: maps endpoint `bus-width` values 12/16/18/24 to RGB444/RGB565/RGB666/RGB888 media bus formats; missing property returns 0.
- `atmel_hlcdc_attach_endpoint()`: finds a bridge for one endpoint, allocates an encoder, reads bus width, assigns possible CRTCs, and attaches the bridge.
- `atmel_hlcdc_create_outputs()`: scans endpoints, always trying the first four and then continuing while attachments keep succeeding.

## Control Flow

Output creation iterates endpoint indices. Each endpoint lookup obtains a bridge from OF graph, allocates a simple encoder, obtains the endpoint node to parse `bus-width`, validates the result, links the encoder to the controller CRTC, and attaches the downstream bridge. A missing endpoint is skipped for the first few indices; after at least one success, a trailing `-ENODEV` is treated as success.

## State And Persistence Behavior

The persistent state is the allocated encoder plus its `bus_fmt`. No hardware registers are written directly; later CRTC checks use this state to select controller output mode.

## Dependencies And Integration Points

It depends on OF graph, DRM bridge helpers, simple encoder allocation, and local CRTC/device state. It integrates with downstream panel/bridge drivers and with `atmel_hlcdc_crtc_select_output_mode()`.

## Risks And Edge Cases

The function assumes `devm_drm_of_get_bridge()` returning `-ENODEV` means absent endpoint, not fatal topology damage. Invalid `bus-width` aborts output creation. `DRM_MODE_ENCODER_NONE` is used for the local simple encoder because the downstream bridge determines the physical interface.

## Test Signals

Device-tree graph tests with one or multiple endpoints, missing endpoint gaps, invalid bus widths, RGB444/565/666/888 bus-format negotiation, and downstream bridge attach failures validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c

## Purpose

`atmel_hlcdc_plane.c` implements DRM planes for Atmel HLCDC/XLCDC layers. It handles format support, atomic plane validation, scaling, rotation stride calculation, DMA descriptor allocation/programming, color lookup tables, color-space conversion, blending, discard areas, AHB load balancing, and layer IRQ diagnostics.

## Important APIs, Types, And Functions

- `struct atmel_hlcdc_plane_state`: extends DRM plane state with clipped source/destination geometry, discard rectangle, AHB id, bytes-per-pixel, per-plane DMA offsets/strides, plane count, and allocated DMA descriptors.
- Format tables `atmel_hlcdc_plane_rgb_formats` and `atmel_hlcdc_plane_rgb_and_yuv_formats`.
- `atmel_hlcdc_format_to_plane_mode()`: maps DRM fourcc formats to HLCDC hardware format fields.
- Scaler paths: `atmel_hlcdc_plane_setup_scaler()` for legacy HLCDC with optional PHI coefficients and `atmel_xlcdc_plane_setup_scaler()` for XLCDC luma/chroma factors.
- Atomic helpers: `atmel_hlcdc_plane_atomic_check()`, `_update()`, `_disable()`, state reset/duplicate/destroy.
- Preparation helpers exported to the CRTC: `atmel_hlcdc_plane_prepare_disc_area()` and `atmel_hlcdc_plane_prepare_ahb_routing()`.
- DMA helpers: descriptor pool creation in `atmel_hlcdc_create_planes()`, allocation in `atmel_hlcdc_plane_alloc_dscrs()`, and buffer programming in legacy/XLCDC update callbacks.
- Operation tables `atmel_hlcdc_ops` and `atmel_xlcdc_ops`.

## Control Flow

Plane creation allocates a universal DRM plane for each usable layer descriptor, initializes properties based on layer capabilities, and installs helper funcs. Atomic check clips/scales through DRM helpers, derives integer source/destination geometry, computes per-plane DMA offsets and x/p strides for 0/90/180/270 rotation, swaps source width/height for rotated modes, rejects unsupported scaling or partial-size base layers, and stores derived state. CRTC atomic check then chooses discard and AHB routing. Atomic update writes size/position/scaler, general settings, format, CLUT, buffer addresses/strides, discard registers, and finally enables or updates the layer via the descriptor-selected ops.

## State And Persistence Behavior

Persistent software state includes allocated DMA descriptors for each plane state, per-plane derived geometry and DMA offsets, the controller's descriptor pool, and the `dc->layers[]` mapping. Hardware state persists in layer CFG registers, DMA descriptor rings, CLUT entries, CSC coefficients, scaler coefficients, interrupt masks, enable/update bits, and XLCDC ATTRE update triggers.

## Dependencies And Integration Points

The file depends on DRM atomic helpers, GEM DMA framebuffer helpers, DMA pools, blend/rotation properties, local descriptor/register definitions, and the CRTC's atomic preparation calls. It integrates with the controller IRQ handler through `atmel_hlcdc_plane_irq()`.

## Risks And Edge Cases

DMA descriptors are allocated per atomic state copy; allocation failures can make state duplication fail. Rotation stride math uses negative strides and must account for chroma subsampling. Scaling with alpha formats is rejected because hardware constraints do not allow it. The discard-area optimization only chooses the largest opaque overlay and is intentionally simple. XLCDC updates require writing ATTRE bits for multiple layers, so wrong update masks can leave changes unapplied. Error handling in `anx6345_start`-style sequence is not relevant here, but register writes in this file mostly assume regmap success.

## Test Signals

Atomic plane tests across all supported formats, multi-plane YUV with subsampling, rotations, scaling up/down, alpha blending, CLUT updates, CSC output, discard optimization, AHB routing under multiple planes, DMA descriptor leak checks, layer overrun IRQ logging, and both legacy/XLCDC hardware are important validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Kconfig

## Purpose

`bridge/Kconfig` defines the top-level DRM bridge framework symbols and the menu of individual display bridge drivers. It also sources subdirectory Kconfig files for Analogix, ADV7511, Cadence, i.MX, and Synopsys bridge families.

## Important APIs, Types, And Symbols

Key symbols in this file include framework options `DRM_BRIDGE`, `DRM_PANEL_BRIDGE`, `DRM_AUX_BRIDGE`, and `DRM_AUX_HPD_BRIDGE`, plus many concrete bridge drivers such as Chipone ICN6211, Chrontel CH7033, ChromeOS EC ANX7688, display-connector, FSL LDB, NXP TDA998X, INNO HDMI, ITE IT6263/IT6505/IT66121, Lontium LT8912B/LT9211/LT9611/LT9611UXC/LT8713SX, LVDS codec, Microchip LVDS serializer, Northwest Logic MIPI DSI, Parade PS8622/PS8640, Samsung DSIM, Silicon Image bridges, simple bridge, Toshiba bridges, TI bridges, and Waveshare DSI.

## Control Flow

There is no runtime control flow. Kconfig dependencies and selects determine which bridge objects are compiled and which helper subsystems are selected.

## State And Persistence Behavior

The state is the kernel configuration. Enabling symbols persists in `.config` and affects built-in/module outputs, not runtime driver state directly.

## Dependencies And Integration Points

The file depends on DRM and OF for most platform bridges and selects helper frameworks such as DRM KMS helpers, panel bridges, MIPI DSI, DP/HDMI helpers, regmap I2C/MMIO, CEC/audio helpers, auxiliary bus, Type-C, extcon, crypto, and PHY subsystems as needed by each bridge.

## Risks And Edge Cases

Incorrect dependencies can expose drivers on builds that lack required subsystems or hide valid COMPILE_TEST coverage. `select` can force helper subsystems without their optional runtime dependencies, so bridge entries must be precise. Subdirectory `source` lines are required for family-specific drivers to appear.

## Test Signals

Kconfig allmodconfig/allyesconfig, targeted symbol enablement, dependency linting, and verifying Makefile objects are reachable from every symbol are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile

## Purpose

`bridge/Makefile` maps DRM bridge Kconfig symbols to bridge driver objects and descends into bridge-family subdirectories.

## Important APIs, Types, And Targets

- Direct object mappings for many bridge drivers such as `aux-bridge.o`, `chipone-icn6211.o`, `display-connector.o`, `inno-hdmi.o`, `lontium-*`, `sii902x.o`, `tc358*`, TI bridge drivers, and others.
- Composite `tda998x-y := tda998x_drv.o`.
- Subdirectory descent: `adv7511/` under `CONFIG_DRM_I2C_ADV7511`, and unconditional `analogix/`, `cadence/`, `imx/`, and `synopsys/` directories.

## Control Flow

There is no runtime flow. Kbuild uses `obj-$(CONFIG_*)` variables to include objects and subdirectories in the kernel build.

## State And Persistence Behavior

The Makefile only affects build outputs. It stores no runtime state.

## Dependencies And Integration Points

It integrates with the Kconfig symbols in `bridge/Kconfig` and family Kconfig files. The unconditional `obj-y` subdirectories rely on their internal Makefiles to gate individual objects.

## Risks And Edge Cases

Kconfig/Makefile symbol mismatches lead to enabled drivers not building or dead objects that never build. Composite module variables must match the target object name. Unconditional subdir traversal increases the need for correct gating inside subdirectories.

## Test Signals

Build tests for each bridge symbol, `make drivers/gpu/drm/bridge/`, allmodconfig, and checking that Kconfig help/module names match produced objects validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig

## Purpose

This Kconfig file defines build options for the Analog Devices ADV7511/ADV7513/ADV7533/ADV7535 HDMI bridge driver and optional audio/CEC support.

## Important APIs, Types, And Symbols

- `DRM_I2C_ADV7511`: tristate main encoder/bridge driver; depends on OF and selects KMS, regmap I2C, MIPI DSI, display helpers, bridge connector, and HDMI state helper support.
- `DRM_I2C_ADV7511_AUDIO`: optional bool for HDMI audio, depends on the main driver and `SND_SOC`, selects `SND_SOC_HDMI_CODEC`.
- `DRM_I2C_ADV7511_CEC`: optional bool for HDMI CEC, depends on the main driver, selects DRM HDMI CEC helper, and defaults to enabled.

## Control Flow

There is no runtime flow. These symbols control which objects from the local Makefile are linked and which optional hooks compile into `adv7511.h`.

## State And Persistence Behavior

The selected symbols persist in kernel configuration and determine module capabilities.

## Dependencies And Integration Points

The main driver integrates with DRM bridge/connector/HDMI helpers, I2C regmap, MIPI DSI for ADV7533/7535, ASoC HDMI codec for audio, and DRM HDMI CEC helper for CEC.

## Risks And Edge Cases

Audio and CEC are bool options tied to the main driver rather than separate modules. Enabling ADV7533 support selects MIPI DSI even when only ADV7511 parallel RGB hardware is used. CEC defaults on, so missing CEC clock/device-tree support must degrade gracefully.

## Test Signals

Build matrix for main only, main+audio, main+CEC, and all enabled; probe on ADV7511 and ADV7533/7535 device trees; HDMI audio and CEC adapter registration tests validate the options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile

## Purpose

The ADV7511 Makefile defines the composite bridge module and conditionally adds audio and CEC implementation objects.

## Important APIs, Types, And Targets

- `adv7511-y := adv7511_drv.o adv7533.o`: always includes the main driver and ADV7533/7535 DSI companion.
- `adv7511-$(CONFIG_DRM_I2C_ADV7511_AUDIO) += adv7511_audio.o`.
- `adv7511-$(CONFIG_DRM_I2C_ADV7511_CEC) += adv7511_cec.o`.
- `obj-$(CONFIG_DRM_I2C_ADV7511) += adv7511.o`.

## Control Flow

No runtime flow exists here. Kbuild composes `adv7511.o` from the selected objects.

## State And Persistence Behavior

Only build artifacts are affected.

## Dependencies And Integration Points

The object list matches optional function prototypes/stubs in `adv7511.h` and Kconfig symbols in the same directory.

## Risks And Edge Cases

Optional object omission must match stub definitions; otherwise bridge funcs would reference missing symbols. `adv7533.o` is always built with the main driver because chip variants share the module.

## Test Signals

Compile with audio/CEC on and off, run modpost, and load the module on ADV7511 and ADV7533/7535 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511.h

## Purpose

`adv7511.h` is the shared hardware and driver contract for the Analog Devices ADV7511 family bridge driver. It defines register addresses, bit fields, packet/CEC register layouts, link configuration types, chip metadata, main device state, and optional audio/CEC/DSI function prototypes.

## Important APIs, Types, And Macros

- Register macros for main, EDID, packet, CEC, audio, HDMI infoframe, HDCP, power, status, interrupt, and timing-generation registers.
- Bit fields for interrupts, power, HDMI/DVI mode, audio sources/formats/sample rates, packet enables, HPD source/override, and CEC controls.
- `enum adv7511_input_clock`, `adv7511_input_justification`, `adv7511_input_sync_pulse`, `adv7511_sync_polarity`, `adv7511_csc_scaling`, and `adv7511_type`.
- `struct adv7511_link_config`, `struct adv7511_video_config`, `struct adv7511_chip_info`, and central `struct adv7511`.
- `bridge_to_adv7511()` conversion helper.
- Optional CEC/audio prototypes that become `NULL` stubs when Kconfig options are disabled.
- ADV7533/7535 DSI companion APIs for power, timing generator, mode validation, register patching, DSI attach, and DT parsing.

## Control Flow

The header itself has no runtime flow beyond the container helper and conditional prototypes. It shapes control flow in `adv7511_drv.c`: chip info selects link-config parsing vs ADV7533 DSI parsing, CEC register offset, supply names, mode limits, and HPD override behavior.

## State And Persistence Behavior

`struct adv7511` persists all driver state: I2C clients/regmaps, connector status, power flag, current mode, TMDS/audio rates, EDID segment/cache, waitqueue/work item, bridge object, sync/input flags, GPIO/regulators, DSI host/device parameters, chip info, CEC logical addresses, and CEC clock state.

## Dependencies And Integration Points

It depends on Linux HDMI, I2C, regmap, regulators, DRM bridge/connector/MIPI DSI/modes, and optional media CEC/audio headers through implementation files. It is included by all ADV7511 family source files.

## Risks And Edge Cases

Register offsets are hardware ABI values and differ for ADV7533 CEC via `reg_cec_offset`. Optional function macros are `NULL`, so bridge function tables must accept absent hooks. The main state mixes power, EDID, CEC, DSI, and bridge data, so lifetime ordering in probe/remove matters. Incorrect chip info can select wrong supplies, clocks, register patches, or mode limits.

## Test Signals

Compile all Kconfig combinations, validate register accesses on ADV7511/7513/7533/7535 hardware, exercise EDID/HPD/audio/CEC/DSI paths, and inspect remove/error-path cleanup for ancillary I2C clients and clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c

## Purpose

`adv7511_audio.c` implements optional HDMI audio hooks for the ADV7511 bridge using the DRM HDMI audio bridge callbacks and ASoC HDMI codec parameters.

## Important APIs, Types, And Functions

- `adv7511_calc_cts_n()`: computes HDMI CTS/N values from TMDS clock and sample rate.
- `adv7511_update_cts_n()`: writes N and manual CTS registers.
- `adv7511_hdmi_audio_prepare()`: validates sample rate, width, and audio interface format; programs audio source, I2S format, bit clock inversion, sample length, sample-rate ID, CTS/N, and audio infoframe.
- `adv7511_hdmi_audio_startup()`: unmutes/enables audio-related packets, marks audio not copyrighted, disables AV mute, and enables SPDIF receiver if selected.
- `adv7511_hdmi_audio_shutdown()`: disables SPDIF receiver when needed and clears the audio infoframe.

## Control Flow

Prepare maps `hdmi_codec_params` and `hdmi_codec_daifmt` to ADV7511 register values, rejecting unsupported rates, widths, or formats. Startup enables packets and receiver state after a valid prepare. Shutdown reverses SPDIF receiver state and removes the advertised audio infoframe.

## State And Persistence Behavior

The file updates `adv7511->audio_source` and `adv7511->f_audio`. It persists audio state in hardware registers for N/CTS, audio source/config, I2S width/format, packet enables, general-control AV mute, and infoframes.

## Dependencies And Integration Points

It depends on ALSA/ASoC HDMI codec types, DRM HDMI state helpers, and register definitions from `adv7511.h`. It is wired into `adv7511_bridge_funcs` only when `CONFIG_DRM_I2C_ADV7511_AUDIO` is enabled.

## Risks And Edge Cases

CTS/N calculation assumes supported HDMI sample rates; unsupported values leave `n` uninitialized if new callers bypass validation. 32-bit samples are accepted only for IEC958 subframes. Startup uses the previously prepared `audio_source`, so calling order matters. Infoframe update failures from DRM helpers propagate only from prepare.

## Test Signals

HDMI audio playback at all supported sample rates and widths, I2S/right-justified/left-justified/SPDIF modes, IEC958 32-bit path, infoframe inspection, audio mute/start/stop cycles, and hotplug with active audio are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c

## Purpose

`adv7511_cec.c` implements optional HDMI CEC support for ADV7511/ADV7533/ADV7535 bridge variants using the DRM HDMI CEC connector helper interface.

## Important APIs, Types, And Functions

- RX register arrays for the three hardware receive buffers and `ADV7511_INT1_CEC_MASK`.
- `adv_cec_tx_raw_status()`: converts TX-ready/arbitration-lost/retry-timeout interrupt bits and low-drive counters into CEC transmit completion status.
- `adv7511_cec_rx()`: reads one RX buffer, clamps length to 16, clears/re-enables that buffer, and delivers the message.
- `adv7511_cec_irq_process()`: handles TX status and RX buffers in hardware timestamp order.
- `adv7511_cec_enable()`: powers CEC up/down, clears RX buffers, enables/disables CEC IRQs, and resets logical-address state.
- `adv7511_cec_log_addr()`: programs up to three logical address masks.
- `adv7511_cec_transmit()`: sets retry count, clears TX IRQs, writes the CEC frame, length, and transmit-enable bit.
- `adv7511_cec_init()`: obtains/enables the CEC clock, resets CEC, configures non-legacy RX mode and clock divider, and stores the DRM connector.

## Control Flow

CEC init prepares the hardware block and leaves it powered down if the CEC clock is unavailable except for probe deferral. Enabling powers the block, clears RX buffers, disables TX, and enables main interrupt bits. IRQ processing first reports TX completion if relevant, then reads `CEC_RX_STATUS` to reconstruct oldest-to-newest RX buffer order before delivering messages. Transmit writes the full frame before setting TX enable.

## State And Persistence Behavior

Software state includes `cec_connector`, `cec_enabled_adap`, up to three logical addresses in `cec_addr[]`, `cec_valid_addrs`, and CEC clock frequency. Hardware state persists in CEC clock divider, RX buffer controls, TX frame registers, logical-address masks, and main interrupt enable/status registers.

## Dependencies And Integration Points

It depends on media CEC constants, DRM HDMI CEC helper callbacks, clocks, regmap, and ADV7511 chip-info `reg_cec_offset` for ADV7533-style register windows. The main driver calls its IRQ processor from shared interrupt handling.

## Risks And Edge Cases

Only three logical addresses are supported. `adv7511_cec_init()` returns success for non-deferral clock errors after powering CEC down, so CEC can be silently unavailable. RX length is clamped but malformed zero-length frames are ignored. The retry register uses at least one retry even when attempts is one because hardware semantics are unclear.

## Test Signals

CEC adapter registration, logical address allocation/clear, transmit OK/NACK/arbitration/timeout statuses, receiving multiple queued messages in order, CEC enable/disable cycles, ADV7511 and ADV7533 offset coverage, and missing-clock behavior are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c

## Purpose

`adv7511_drv.c` is the main DRM bridge and I2C driver for Analog Devices ADV7511/ADV7513/ADV7533/ADV7535 HDMI transmitters. It handles register-map setup, hardware patches, power/HPD/EDID, video mode programming, HDMI infoframes, optional bridge connector creation, CEC regmap setup, regulator/GPIO setup, DSI companion attachment, and module registration.

## Important APIs, Types, And Functions

- Register data: `adv7511_fixed_registers`, `adv7511_register_defaults`, volatile-register predicate, and regmap configs for main, packet, and CEC maps.
- Video helpers: `adv7511_set_colormap()`, packet enable/disable, `adv7511_set_config_csc()`, `adv7511_set_link_config()`, and `adv7511_mode_set()`.
- Power/HPD/EDID helpers: `__adv7511_power_on/off()`, `adv7511_power_on/off()`, `adv7511_hpd_work()`, `adv7511_irq_process()`, `adv7511_wait_for_edid()`, `adv7511_get_edid_block()`, `adv7511_edid_read()`, and `adv7511_detect()`.
- DRM bridge funcs: atomic enable/disable, mode/TMDS validation, attach, detect, EDID read, HDMI infoframe clear/write hooks, optional audio hooks, and optional CEC hooks.
- Probe/remove: regulator init, ancillary EDID/packet/CEC I2C devices, chip-specific register patching, DT parsing, bridge registration, IRQ request, and ADV7533 DSI attach.
- Chip metadata for ADV7511, ADV7533, and ADV7535 plus I2C/OF IDs and module init/exit that registers both MIPI DSI and I2C drivers when configured.

## Control Flow

Probe validates OF data, allocates the bridge object, finds downstream bridge, parses either parallel RGB link config or ADV7533 DSI DT, enables supplies and optional powerdown GPIO, creates regmaps and ancillary I2C clients, applies chip patches, initializes CEC regmap, powers the chip off into a clean cached state, configures bridge ops and optional audio/CEC metadata, registers the bridge, requests IRQ, and attaches DSI for ADV7533/7535. Atomic enable powers on, retrieves connector and CRTC state, configures CSC/output mode, programs timing, and updates HDMI infoframes. Atomic disable powers off. EDID reads temporarily power the chip if needed and fetch 256-byte EDID segments via four 64-byte I2C reads. IRQ handling acknowledges INT0/INT1, schedules HPD work, wakes EDID waits, and dispatches CEC.

## State And Persistence Behavior

Persistent software state is the `struct adv7511` allocated with the bridge: power flag, connector status, current mode, TMDS clock, EDID cache/segment, waitqueue/work item, input color/sync flags, ancillary I2C clients/regmaps, regulator array, DSI state, and CEC state. Hardware state persists in ADV7511 registers but many registers reset on powerdown or HPD low; the driver uses regcache dirty/sync to restore cached state.

## Dependencies And Integration Points

The driver depends on I2C, regmap cache, regulators, optional GPIO, OF graph, DRM bridge/bridge-connector/HDMI state helpers, EDID helpers, optional ASoC audio, optional CEC, and MIPI DSI for ADV7533/7535. It integrates with downstream bridges through `drm_of_find_panel_or_bridge()` and `drm_bridge_attach()`.

## Risks And Edge Cases

The chip can reset registers on unplug, so HPD handling must mark regcache dirty and repower to restore state. EDID retrieval supports IRQ and polling paths; missed interrupts or DDC errors surface as `-EIO`. Link-config DT parsing is strict about depth, colorspace, clock style, input style, justification, and clock delay. Error paths must unregister ancillary I2C clients and disable CEC clocks/regulators in the right order. ADV7535 HPD override behavior differs from other variants. Infoframe writes assume buffers include the HDMI packet type byte and bulk-write `buffer + 1`.

## Test Signals

Probe/remove error-path tests, EDID read with IRQ and polling, HPD plug/unplug while powered, DVI vs HDMI sink mode, YCbCr-to-RGB CSC and YCbCr422 output, low-refresh modes, infoframe contents, TMDS clock limits, ADV7533/7535 DSI mode validation/attach, suspend-like power cycles, audio/CEC Kconfig combinations, and regcache restoration after HPD reset are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7533.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7533.c

## Purpose

`adv7533.c` provides ADV7533/ADV7535-specific support for the ADV7511 family driver, covering MIPI DSI input setup, timing generator programming, chip-specific register patches, DSI mode validation, DSI device attachment, and device-tree parsing.

## Important APIs, Types, And Functions

- `adv7533_fixed_registers` and `adv7533_cec_fixed_registers`: chip-specific register patches.
- `adv7533_dsi_config_timing_gen()`: programs horizontal/vertical timing-generator registers from `adv->curr_mode` and DSI lane count.
- `adv7533_dsi_power_on()` / `_power_off()`: configure lane count, timing generator reset/disable, HDMI enable/test mode, and CEC-side patches.
- `adv7533_mode_valid()`: checks pixel clock times bits-per-pixel against maximum lane frequency times lane count.
- `adv7533_patch_registers()` and `_patch_cec_registers()`: apply register patches.
- `adv7533_attach_dsi()`: finds the MIPI DSI host, creates a DSI peripheral, sets lanes/RGB888/video flags, and attaches to host.
- `adv7533_parse_dt()`: reads `adi,dsi-lanes`, remote host node, timing-generator flag, and defaults RGB/non-embedded-sync input state.

## Control Flow

DT parsing runs during main probe for DSI variants. Later `adv7533_attach_dsi()` defers until the host exists, registers a DSI device, and attaches it. During bridge power-on, DSI parameters and timing-generator state are programmed. When the main driver sets a mode and timing generator is enabled, timing registers are updated from the current mode.

## State And Persistence Behavior

The file updates `adv->num_dsi_lanes`, `host_node`, `use_timing_gen`, `rgb`, `embedded_sync`, and `dsi`. Hardware state persists in the CEC-side register window for DSI lane count, timing generator, HDMI enable, and timing parameters.

## Dependencies And Integration Points

It depends on OF graph, MIPI DSI helpers, DRM display modes, and the shared ADV7511 state/regmaps. The main driver calls these hooks based on chip info `has_dsi`.

## Risks And Edge Cases

Only 2-4 DSI lanes are accepted, and `clock_div_by_lanes[dsi->lanes - 2]` relies on that validation. Mode validation assumes RGB888 bpp from the attached DSI format. Missing DSI host returns probe deferral. Timing register writes use packed high/low nibbles and are sensitive to mode values.

## Test Signals

ADV7533 and ADV7535 probe with 2/3/4-lane DTs, DSI host deferral, mode-clock limit tests, timing generator enabled/disabled display output, register patch verification, and power cycle tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7533.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig

## Purpose

`analogix/Kconfig` defines Analogix DRM bridge options for ANX6345, ANX78XX, the shared Analogix DP core, and ANX7625.

## Important APIs, Types, And Symbols

- `DRM_ANALOGIX_ANX6345`: OF-based ANX6345 bridge, selecting Analogix DP helpers, DRM DP/display helpers, KMS helpers, and regmap I2C.
- `DRM_ANALOGIX_ANX78XX`: SlimPort/MyDP bridge with the shared Analogix DP and helper selections.
- `DRM_ANALOGIX_DP`: tristate shared DP core depending on DRM.
- `DRM_ANALOGIX_ANX7625`: MIPI/DPI-to-DP bridge depending on DRM, OF, Type-C, USB role switch, and selecting DP/HDCP/display helpers, DP AUX bus, and MIPI DSI.

## Control Flow

There is no runtime control flow. Kconfig symbols control which objects in `analogix/Makefile` are built and which helpers are selected.

## State And Persistence Behavior

The only state is kernel configuration.

## Dependencies And Integration Points

The symbols integrate Analogix bridge drivers with DRM DP helpers, regmap I2C, KMS, Type-C/USB-role infrastructure, HDCP helpers, and MIPI DSI depending on the chip.

## Risks And Edge Cases

The hidden shared `DRM_ANALOGIX_DP` core is selected by front-end drivers. Missing OF or Type-C dependencies should prevent invalid runtime configurations. Helper selection must stay aligned with source includes and Makefile targets.

## Test Signals

Kconfig build matrix, allmodconfig, and targeted module builds for each Analogix symbol validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile

## Purpose

The Analogix bridge Makefile maps Analogix Kconfig symbols to their driver objects and defines the shared Analogix DP composite object.

## Important APIs, Types, And Targets

- `analogix_dp-objs := analogix_dp_core.o analogix_dp_reg.o analogix-i2c-dptx.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX6345) += analogix-anx6345.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX7625) += anx7625.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_ANX78XX) += analogix-anx78xx.o`.
- `obj-$(CONFIG_DRM_ANALOGIX_DP) += analogix_dp.o`.

## Control Flow

No runtime flow exists. Kbuild composes and links objects based on Kconfig.

## State And Persistence Behavior

The file only affects build outputs.

## Dependencies And Integration Points

It integrates the local Kconfig symbols with the shared DP core and chip-specific I2C bridge drivers.

## Risks And Edge Cases

If a chip driver selects `DRM_ANALOGIX_DP` but the composite object list misses a required helper, link failures or missing AUX operations can result. Symbol/filename mismatches make Kconfig entries ineffective.

## Test Signals

Build each Analogix bridge as module and built-in, verify `analogix_dp.o` composition, and run modpost for unresolved symbol coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c

## Purpose

`analogix-anx6345.c` implements an I2C DRM bridge driver for the Analogix ANX6345 LVTTL RGB to eDP/DisplayPort transmitter. It manages dual I2C register maps, power sequencing, AUX/DDC access, DP link training, connector creation, EDID retrieval, panel integration, and bridge enable/disable.

## Important APIs, Types, And Functions

- `struct anx6345`: stores DP AUX, bridge, main I2C client, EDID cache, connector, optional panel, regulators, reset GPIO, EDID mutex, two I2C clients/regmaps, chip ID, DPCD cache, and power flag.
- Register-map helpers `anx6345_set_bits()` and `anx6345_clear_bits()`.
- `anx6345_aux_transfer()`: delegates DP AUX transactions to `anx_dp_aux_transfer()`.
- `anx6345_dp_link_training()`: powers link logic, reads DPCD/link bandwidth, configures downspread/enhanced framing/lane count/link rate, writes sink DPCD, starts source training, and polls training completion.
- `anx6345_tx_initialization()`: programs video input depth, PLL/debug/power, forced HPD, lane training controls, and resets AUX.
- `anx6345_poweron()` / `_poweroff()`: sequence reset GPIO, `dvdd12`/`dvdd25` regulators, module power bits, panel prepare/unprepare, and the power flag.
- Bridge/connector funcs: attach/detach, mode_valid, enable/disable, connector get_modes/destroy/atomic funcs.
- Probe/remove: allocate bridge, find panel, get supplies/reset GPIO, create dummy I2C clients and regmaps, power on, validate chip ID, add bridge, and cleanup.

## Control Flow

Probe builds both register maps for DPTX and TX common address windows, powers the chip, reads chip ID/version, and registers the bridge on success. Bridge attach registers DP AUX, initializes and registers an eDP connector, and attaches it to the encoder. Mode enumeration powers the chip temporarily if needed, checks sink count, reads EDID over DP AUX DDC, updates connector EDID, and falls back to panel modes if EDID yields none. Bridge enable enables the panel, starts the transmitter, runs link training, then unmutes/enables DP output. Disable powers down video/link/audio/HDCP modules, disables panel, and powers off regulators.

## State And Persistence Behavior

Software state includes EDID cache protected by `lock`, DPCD cache, chip ID, power flag, registered AUX/connector, panel pointer, regulators/GPIO, and dummy I2C clients. Hardware state persists in ANX6345 power, PLL, video, link-training, lane, downspread, AUX, and DP stream-control registers, plus sink DPCD settings.

## Dependencies And Integration Points

It depends on DRM bridge/connector/EDID/DP helpers, Analogix I2C DPTX/TX common register headers, I2C, regmap, regulators, GPIO, optional panel, OF graph, and DP AUX/DDC infrastructure. It presents a DRM bridge with its own connector; it rejects `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.

## Risks And Edge Cases

The power-on path returns void and logs regulator failures, so callers may continue after partial power failure. `anx6345_start()` overwrites the first `clear_bits()` return by immediately calling TX initialization, losing that specific error. The driver currently hardcodes 6 bpc and rejects clocks above 154 MHz/interlace. It forces HPD/stream validity and only supports DPCD link rates 1.62 and 2.7 Gbps. EDID is cached until remove and may become stale after downstream changes.

## Test Signals

Probe with both possible I2C base addresses, regulator/reset sequencing, chip ID detection, AUX registration, EDID read and panel fallback, DP link training at 1.62/2.7 Gbps, mode rejection for interlace/high clock, enable/disable cycles, hotplug/panel tests, and cleanup of dummy I2C clients/EDID cache are important validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c -->
