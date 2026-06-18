# Research: subset-b-003544

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_wb_connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_wb_connector.c

## Purpose

`komeda_wb_connector.c` implements Komeda DRM writeback connector support. It exposes a virtual always-connected writeback connector per CRTC when the master pipeline has a writeback layer, advertises formats supported by that writeback layer, and validates/builds Komeda data-flow state for capturing the composition output into a framebuffer.

## Important APIs, Types, And Functions

The exported API is `komeda_kms_add_wb_connectors()`, which iterates all Komeda CRTCs and calls the internal `komeda_wb_connector_add()`. The connector uses `drm_writeback_connector_init()` with `komeda_wb_connector_funcs` and `komeda_wb_encoder_helper_funcs`. The important validation path is `komeda_wb_encoder_atomic_check()`, which checks for an active CRTC, fetches the target `struct drm_writeback_job`, initializes a `struct komeda_data_flow_cfg` via `komeda_wb_init_data_flow()`, and routes either through `komeda_build_wb_data_flow()` or `komeda_build_wb_split_data_flow()`.

## Control Flow

During KMS initialization, each CRTC with `kcrtc->master->wb_layer` gets a `struct komeda_wb_connector`. Initialization allocates the wrapper, stores the writeback layer, obtains a FourCC list from the format table for that layer type, registers the writeback connector with a possible-CRTC mask for the owning CRTC, attaches connector helpers, and fills display-info color depth/format capabilities from the pipeline improc block. During an atomic commit check, no writeback job means no work. A job on an inactive CRTC fails. A job on an active CRTC builds a data-flow description where the input comes from the pipeline compiz output and the output dimensions come from the writeback framebuffer.

## State And Persistence Behavior

Persistent driver state is limited to the allocated `struct komeda_wb_connector`, its `wb_layer` pointer, and `kcrtc->wb_conn`. Per-commit data-flow state is temporary and lives in atomic state objects. The connector is always reported connected, has no modes of its own, and accepts modes only within `drm_mode_config` min/max dimensions. Destroy cleans up the DRM connector and frees the wrapper.

## Dependencies And Integration Points

This file integrates Komeda KMS objects, Komeda pipeline composition helpers, layer format-table helpers, DRM writeback core, DRM atomic connector/encoder helpers, and Komeda data-flow builders. It depends on the surrounding Komeda pipeline model: compiz is the source for captured frames, the writeback layer is the sink, and split writeback is delegated to Komeda data-flow construction.

## Risks And Edge Cases

The atomic check mutates `crtc_st->connectors_changed` when the only connector change is the writeback connector; mistakes here can trigger unnecessary modesets or skip required ones. The code assumes `conn_st->writeback_job->fb` is valid when `writeback_job` is non-NULL. Format-list allocation and connector registration failures must free the wrapper and return promptly. Split data-flow handling is selected from `dflow.en_split`, so correctness depends on `komeda_complete_data_flow_cfg()`.

## Test Signals

Useful signals include Komeda probe with pipelines that both have and lack a writeback layer, writeback jobs for every advertised writeback format, inactive-CRTC writeback rejection, writeback-only atomic commits that do not force a modeset, split and non-split writeback coverage, connector cleanup on bind failure/unbind, and IGT writeback tests validating captured frame dimensions and contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_wb_connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_crtc.c

## Purpose

`hdlcd_crtc.c` implements the CRTC and primary-plane side of the ARM HDLCD DRM driver. HDLCD is modeled as a simple RGB scanout engine with one primary plane and no scaling, with mode timing, pixel format, framebuffer address, pitch, and vblank interrupt enable programmed directly into HDLCD registers.

## Important APIs, Types, And Functions

The file exports `hdlcd_setup_crtc()`. Internally, `hdlcd_plane_init()` creates the primary plane, and `drm_crtc_init_with_planes()` wires it to `hdlcd_crtc_funcs` and `hdlcd_crtc_helper_funcs`. `supported_formats[]` maps DRM FourCC formats to `struct pixel_format` descriptions from `video/pixel_format.h`. `hdlcd_set_pxl_fmt()` programs `HDLCD_REG_PIXEL_FORMAT` and color selector registers. `hdlcd_crtc_mode_set_nofb()` programs timing, bus options, polarities, and pixel clock rate. `hdlcd_plane_atomic_update()` programs line length, pitch, line count, and scanout base.

## Control Flow

CRTC setup allocates a universal primary plane, attaches plane helpers, initializes the CRTC, and attaches CRTC helpers. Atomic checking for the plane rejects line counts beyond `HDLCD_MAX_YRES`, rejects disabling the only plane while the CRTC remains active, and uses `drm_atomic_helper_check_plane_state()` with no scaling. Atomic enable prepares the pixel clock, writes mode registers, enables the controller command bit, and turns vblank accounting on. Atomic disable reverses that order by turning vblank off, clearing command, and disabling the clock. Atomic begin handles pending vblank events by arming them if vblank can be acquired or sending immediately on failure.

## State And Persistence Behavior

CRTC and plane state are DRM-managed atomic objects, while hardware state persists in MMIO registers until mode changes, plane updates, disable, cleanup, or reset. `hdlcd->plane` stores the primary plane pointer. The pixel clock is set to `crtc_clock * 1000` in `hdlcd_crtc_mode_set_nofb()` after programming timing. Cleanup stops the controller by writing zero to `HDLCD_REG_COMMAND`.

## Dependencies And Integration Points

The implementation depends on DRM atomic helpers, DRM fb DMA/GEM DMA helpers for physical scanout addresses, OF graph and clock infrastructure, HDLCD register macros, and `struct hdlcd_drm_private` accessors from `hdlcd_drv.h`. It integrates with the top-level HDLCD probe in `hdlcd_drv.c`, which provides MMIO, clock, IRQ, mode-config, and external encoder component binding.

## Risks And Edge Cases

`hdlcd_set_pxl_fmt()` returns success after `WARN_ON(!format)`, so bad formats should be prevented by plane format advertisement. The plane check debug text says source width but validates height. The driver assumes one active primary plane and no scaling. Register timing values are written as minus-one fields, so zero porch/sync values would underflow if accepted by earlier mode validation. Vblank event handling depends on IRQ installation and correct interrupt mask management.

## Test Signals

Relevant validation includes KMS atomic modeset/page-flip tests, each supported format, max/min resolution boundaries, clock-rounding rejection, vblank enable/disable and event delivery tests, suspend/resume through the parent driver, DMA scanout address correctness for cropped primary-plane state, and underrun visibility when `CONFIG_DRM_HDLCD_SHOW_UNDERRUN` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.c

## Purpose

`hdlcd_drv.c` is the top-level ARM HDLCD platform DRM driver. It owns device allocation, MMIO mapping, hardware identity checks, clock/resource setup, IRQ installation, mode-config setup, component binding to an external encoder, vblank initialization, debugfs counters, runtime/system power hooks, and DRM device registration.

## Important APIs, Types, And Functions

The driver defines `hdlcd_driver`, `hdlcd_mode_config_funcs`, `hdlcd_master_ops`, and `hdlcd_platform_driver`. Probe is split between `hdlcd_probe()`, which builds a component-master match from OF graph port 0, and `hdlcd_drm_bind()`, which allocates `struct hdlcd_drm_private`, initializes mode config, calls `hdlcd_load()`, binds child components, registers vblank, and registers the DRM device. `hdlcd_irq()` services VSYNC and optional debug interrupts. Debugfs exposes `interrupt_count` and `clocks` when enabled.

## Control Flow

Probe obtains the remote output node and registers a component master. Bind allocates the DRM device, initializes mode-config limits and callbacks, then `hdlcd_load()` gets the `pxlclk`, maps MMIO, validates `HDLCD_REG_VERSION`, initializes optional reserved memory, sets a 32-bit DMA mask, creates the CRTC, gets the IRQ, and installs the handler. Bind then stores the CRTC output port, binds external components, enables runtime PM, initializes vblank, disables any firmware-left-enabled controller and removes conflicting aperture users, resets mode config, initializes polling, adds debugfs files, registers the DRM device, and starts the DRM client setup. Unbind unregisters and shuts down in reverse.

## State And Persistence Behavior

`struct hdlcd_drm_private` stores MMIO, clock, CRTC, plane pointer, IRQ number, and optional atomic interrupt counters. Hardware state persists in HDLCD registers until atomic commits, IRQ acknowledgement, cleanup, or disable. Reserved-memory attachment persists for the device lifetime. Runtime PM state is enabled after component binding and disabled during unbind/error paths. Debug counters are in-memory atomics reset at load.

## Dependencies And Integration Points

The file integrates Linux platform devices, OF graph, component framework, reserved memory, DMA mask setup, aperture takeover, DRM atomic/modeset/vblank/client helpers, fbdev DMA helper ops, GEM DMA helper ops, HDLCD CRTC setup, and an external encoder component discovered through DT. It depends on register definitions from `hdlcd_regs.h` and private state/accessors from `hdlcd_drv.h`.

## Risks And Edge Cases

Error unwinding crosses DRM-managed and non-managed resources: IRQ install, reserved memory, CRTC cleanup, component binding, PM enablement, and OF node references must stay balanced. `pm_runtime_get_sync()` in unbind is not checked. Firmware takeover only checks `HDLCD_REG_COMMAND`, so stale register state beyond the command bit may remain until the first modeset. IRQ debug counters are conditional, and debug IRQ mask differs from VSYNC mask used by vblank enable.

## Test Signals

Validation should cover probe/remove, invalid product-id rejection, missing output graph, missing clock/IRQ, reserved-memory success and absence, simplefb/aperture handoff, component bind/unbind failure paths, vblank interrupt delivery, debugfs counter increments, system suspend/resume via DRM mode-config helpers, and DRM client/fbdev setup on systems with and without fbdev emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.h

## Purpose

`hdlcd_drv.h` defines the private state and local helper API shared by the ARM HDLCD driver files. It is a small internal header rather than a hardware register catalog.

## Important APIs, Types, And Functions

The central type is `struct hdlcd_drm_private`, embedding `struct drm_device base` and carrying MMIO base, pixel clock, CRTC, primary plane pointer, IRQ number, and debugfs-only interrupt counters. The helper macros `drm_to_hdlcd_priv()` and `crtc_to_hdlcd_priv()` convert DRM objects back to the private structure. Inline MMIO helpers `hdlcd_write()` and `hdlcd_read()` wrap `writel()` and `readl()` against `hdlcd->mmio + reg`. The header declares `hdlcd_setup_crtc()` and `hdlcd_set_scanout()`.

## Control Flow

This header has no standalone control flow. It supports the bind/load path in `hdlcd_drv.c`, which allocates `struct hdlcd_drm_private`, and the CRTC/plane helpers in `hdlcd_crtc.c`, which repeatedly use the conversion macros and MMIO helpers while programming modes, scanout, and interrupts.

## State And Persistence Behavior

The structure owns process-lifetime driver state for one HDLCD device. Its `base` member ensures the private object is allocated and freed as the DRM device. `mmio`, `clk`, `irq`, `crtc`, and `plane` identify resources used for hardware programming. Debug counters are volatile runtime diagnostics and do not persist across unload or reprobe. Register writes through `hdlcd_write()` persist in hardware until overwritten or reset.

## Dependencies And Integration Points

The header assumes Linux DRM, clock, atomic, and MMIO types are visible through including C files. It integrates the top-level driver and CRTC implementation by providing the shared private type and accessors. `hdlcd_set_scanout()` is declared but not implemented in the listed files, so it is either historical/API residue or implemented outside this subset in another tree version.

## Risks And Edge Cases

MMIO helpers perform no NULL or PM-state checks, so callers must ensure MMIO is mapped and clocks/power are suitable. The embedded DRM-device pattern means incorrect container conversions can corrupt unrelated memory. Any change to `struct hdlcd_drm_private` can affect all call sites using container macros. Conditional debug fields mean code must keep `CONFIG_DEBUG_FS` guards aligned.

## Test Signals

Compile coverage with and without `CONFIG_DEBUG_FS`, sparse or Coccinelle checks for MMIO accessors, probe tests that exercise conversion macros through CRTC and IRQ paths, and header dependency checks are the main signals. A symbol check can confirm whether `hdlcd_set_scanout()` is still needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_regs.h

## Purpose

`hdlcd_regs.h` is the ARM HDLCD register and bit-definition header. It names MMIO offsets for version, interrupt, framebuffer, bus, timing, polarity, command, pixel-format, and color-select registers, plus constants for product identification, interrupt bits, polarity bits, command bits, bus options, and maximum resolution.

## Important APIs, Types, And Macros

Key register offsets include `HDLCD_REG_VERSION`, `HDLCD_REG_INT_*`, `HDLCD_REG_FB_BASE`, `HDLCD_REG_FB_LINE_LENGTH`, `HDLCD_REG_FB_LINE_COUNT`, `HDLCD_REG_FB_LINE_PITCH`, `HDLCD_REG_BUS_OPTIONS`, vertical/horizontal timing registers, `HDLCD_REG_POLARITIES`, `HDLCD_REG_COMMAND`, `HDLCD_REG_PIXEL_FORMAT`, and RGB select registers. Important masks include `HDLCD_PRODUCT_ID`, `HDLCD_PRODUCT_MASK`, version masks, `HDLCD_INTERRUPT_*`, `HDLCD_DEBUG_INT_MASK`, `HDLCD_POLARITY_*`, `HDLCD_COMMAND_ENABLE`, `HDLCD_BYTES_PER_PIXEL_MASK`, bus burst constants, `HDLCD_MAX_XRES`, and `HDLCD_MAX_YRES`.

## Control Flow

The header has no runtime control flow. It is consumed by driver code that validates the product register, installs/acknowledges interrupts, programs framebuffer DMA layout, programs display timings, configures signal polarities, enables/disables the controller, and selects pixel component extraction.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware stateful registers. Writes to timing, bus, framebuffer, pixel-format, and command registers persist until subsequent driver writes, hardware reset, or power loss. Interrupt status/clear/mask registers have side-effect semantics that callers must respect.

## Dependencies And Integration Points

The file is paired with `hdlcd_drv.c` and `hdlcd_crtc.c`. It depends only on the C preprocessor and basic integer constants. It integrates with DRM mode programming by translating DRM timing and format state into HDLCD MMIO fields.

## Risks And Edge Cases

Register values include minus-one encoded dimensions in consumers, so valid ranges must be enforced before writes. Interrupt bits include debug-only signals that should not be confused with the VSYNC vblank mask. `HDLCD_PIXEL_FMT_BIG_ENDIAN` exists but current listed code only programs bytes-per-pixel and component selectors. Maximum resolution is documented as 4096x4096 at 32bpp and should remain synchronized with mode-config limits.

## Test Signals

Useful signals include product ID matching, interrupt-mask and clear behavior on hardware, max-resolution mode rejection/acceptance, all advertised pixel formats producing correct colors, bus burst behavior under high bandwidth, and static comparison against ARM HDLCD hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_crtc.c

## Purpose

`malidp_crtc.c` implements CRTC behavior for the ARM Mali-DP500/DP550/DP650 DRM driver. It validates pixel clocks, manages runtime PM and CRTC enable/disable, performs CRTC-level atomic validation for gamma, CTM, scaling, and rotation-memory budgets, owns custom CRTC state, and wires vblank interrupt enablement.

## Important APIs, Types, And Functions

The exported function is `malidp_crtc_init()`. Important helpers include `malidp_crtc_mode_valid()`, `malidp_crtc_atomic_enable()`, `malidp_crtc_atomic_disable()`, `malidp_crtc_atomic_check()`, `malidp_crtc_atomic_check_gamma()`, `malidp_crtc_atomic_check_ctm()`, `malidp_crtc_atomic_check_scaling()`, and CRTC state reset/duplicate/destroy functions. `struct malidp_crtc_state` carries generated gamma coefficients, color-adjust coefficients, scaling-engine config, and a scaled-plane bitmask.

## Control Flow

Initialization creates display-engine planes, finds the primary plane, initializes the CRTC, enables DRM color management, and programs scaling enhancer coefficients. Atomic mode validation checks exact pixel-clock support. Atomic enable gets runtime PM, converts the adjusted mode to `struct videomode`, enables and sets the pixel clock, calls variant `modeset()`, leaves config mode, and turns vblank on. Atomic disable disables planes, turns vblank off, enters config mode, disables pixel clock, and drops runtime PM. Atomic check first budgets rotation memory across rotated or compressed planes, suppresses modesets for writeback-only connector-mask changes, then validates gamma, CTM, and scaling in sequence.

## State And Persistence Behavior

CRTC state persists in DRM atomic state and is duplicated between commits. Gamma is converted from a 4096-entry monochrome LUT into 64 hardware coefficient-table entries. CTM is converted from S31.32 DRM values to Q3.12-like two's-complement hardware coefficients. Scaling state records source/destination sizes, phase values, selected coefficient sets, source plane ID, and enhancer enable. Hardware config-mode and vblank state are controlled through variant callbacks and IRQ helpers.

## Dependencies And Integration Points

The file depends on DRM atomic helpers, runtime PM, clocks, videomode conversion, Mali-DP private structures, hardware callbacks from `malidp_hw.h`, and writeback connector indexing from `malidp_drv.h`. It integrates with plane checks via `scaled_planes_mask` and `rotmem_size`, and with `malidp_drv.c` commit-tail code that later writes gamma/color/scaling state.

## Risks And Edge Cases

The rotation-memory algorithm depends on DRM plane iteration order placing `DE_VIDEO1` first when needed. Gamma rejects non-monochrome curves and requires exactly `MALIDP_GAMMA_LUT_SIZE`; CTM rejects values outside representable hardware range. Only one plane can use the scaling engine. Pixel clock validation requires exact `clk_round_rate()` equality. `pm_runtime_get_sync()` failure in enable returns without cleanup beyond debug logging.

## Test Signals

Test signals include mode-clock rejection, enable/disable suspend-resume paths, 4096-entry gamma LUT acceptance and invalid-size/color rejection, CTM overflow rejection, single-plane scaling and multi-plane scaling rejection, rotated/compressed plane memory budget failures, writeback-only connector changes avoiding modesets, and vblank enable/disable IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.c

## Purpose

`malidp_drv.c` is the top-level ARM Mali-DP KMS/DRM platform driver. It allocates the DRM device and hardware runtime state, validates the detected IP variant against device-tree, sets up clocks, reserved memory, mode-config, CRTC, planes, writeback, components, IRQs, vblank, PM, debugfs, framebuffer creation, and the custom atomic commit tail.

## Important APIs, Types, And Functions

Key structures are `malidp_driver`, `malidp_mode_config_funcs`, `malidp_mode_config_helpers`, `malidp_drm_of_match`, `malidp_pm_ops`, and `malidp_platform_driver`. Important functions include `malidp_bind()`, `malidp_unbind()`, `malidp_atomic_commit_tail()`, `malidp_set_and_wait_config_valid()`, `malidp_fb_create()`, AFBC framebuffer verification helpers, `malidp_irq_init()`, `malidp_dumb_create()`, runtime PM callbacks, and debugfs error-stat helpers.

## Control Flow

Probe finds an OF output endpoint and registers a component master. Bind allocates `struct malidp_drm`, allocates `struct malidp_hw_device`, maps MMIO, gets pclk/aclk/mclk/pxlclk, attaches optional reserved memory, enables runtime PM, verifies DT compatible string and resource size against hardware ID, queries variant capabilities, programs output color depth and ARQOS, initializes config-valid state and waitqueue, initializes mode config/CRTC/writeback, binds the encoder component, sets possible-clone masks, installs DE/SE IRQs, initializes vblank, registers the DRM device, and starts client setup. The commit tail gets runtime PM, clears config-valid, applies modeset disables, writes gamma/color/scaling state, commits active planes, commits writeback, enables modesets, waits for config-valid completion, releases PM, and cleans planes.

## State And Persistence Behavior

Persistent driver state lives in `struct malidp_drm` and `struct malidp_hw_device`: hardware callbacks, MMIO, clocks, output color depth, runtime PM suspend flag, config-valid atomic, waitqueue, pending event pointer, error statistics, core ID, and memory-write state. Hardware state includes coefficient tables, display function bits, scaling engine registers, plane registers, config-valid flag, output depth, IRQ masks, and clocks. AFBC framebuffer validation checks buffer size and layout before framebuffer creation.

## Dependencies And Integration Points

The file integrates DRM atomic helpers, DRM GEM DMA/fbdev helpers, component framework, OF graph/device matching, reserved memory, runtime/system PM, clocks, debugfs, Mali-DP hardware tables, CRTC/plane initialization, memory writeback, and DE/SE IRQ helpers. Device-tree properties include compatibles, `arm,malidp-arqos-value`, and `arm,malidp-output-port-lines`.

## Risks And Edge Cases

Config-valid wait can time out and retries only five times before logging. Runtime PM transitions must not occur outside config mode. Hardware-ID and resource-size validation are variant-sensitive because DP500 uses different register locations. AFBC verification assumes 16x16 superblocks and one GEM object, checks pitch against width*bpp, and only supports a subset of modifiers. Error unwinding must balance PM, component binding, IRQs, reserved memory, and OF references.

## Test Signals

Important tests include probe on DP500/DP550/DP650 DTs, DT/hardware mismatch rejection, insufficient resource-size rejection, output-port-lines parsing, ARQOS programming, atomic commit event delivery through config-valid IRQ, AFBC framebuffer validation success/failure, runtime/system suspend-resume, debugfs error-stat reset/read, writeback atomic commits, vblank init, and component bind failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.h

## Purpose

`malidp_drv.h` is the internal driver-state header for the ARM Mali-DP DRM driver. It defines the DRM-private object, plane and CRTC extension state, config-valid constants, debug error statistics, helper conversion macros, and local cross-file function declarations.

## Important APIs, Types, And Functions

`struct malidp_drm` embeds `struct drm_device` and stores the hardware device pointer, CRTC, writeback connector, config-valid waitqueue/atomic, pending vblank event, core ID, and debug error stats. `struct malidp_plane` extends `struct drm_plane` with hardware layer metadata. `struct malidp_plane_state` records rotation-memory need, internal format ID, plane count, and MMU prefetch choice. `struct malidp_crtc_state` stores gamma/color-adjust coefficients, scaling-engine config, and scaled-plane mask. The header declares plane/CRTC initialization, format/modifier helpers, error accounting, and the `MALIDP_ROTATED_MASK`.

## Control Flow

The header itself has no runtime control flow. Its constants define the config-valid state machine used by `malidp_drv.c` and `malidp_hw.c`: initial, done, and start/update-in-progress. Container macros connect DRM callbacks back to Mali-DP private objects. Plane and CRTC state structs are allocated and copied by the corresponding atomic reset/duplicate/destroy callbacks.

## State And Persistence Behavior

The types in this header define nearly all persistent software state for a Mali-DP instance. `config_valid` and `wq` coordinate commit completion with DE/DC IRQs. `event` stores a pending flip event until the IRQ path sends it. `rotmem_size`, `format`, and prefetch fields persist across duplicated plane state. Coefficient arrays and scaling config persist in CRTC state until changed by an atomic commit.

## Dependencies And Integration Points

The header depends on DRM writeback/encoder types, waitqueues, mutex/spinlock headers, and `malidp_hw.h`. It integrates `malidp_drv.c`, `malidp_crtc.c`, `malidp_planes.c`, `malidp_hw.c`, and `malidp_mw.c` by providing shared state and declarations.

## Risks And Edge Cases

The header defines cross-file contracts: changing state layout or config-valid constants affects IRQ/commit synchronization. Debug fields are conditional on `CONFIG_DEBUG_FS`. `MALIDP_ROTATED_MASK` covers 90/270 degree rotations but not 180, which matches rotation-memory needs but can be easy to misuse. `malidp_plane_state` fields must be copied during state duplication to avoid stale hardware programming.

## Test Signals

Compile coverage with and without debugfs, atomic state duplicate/reset tests, lockdep around error stats, config-valid wait/IRQ tests, rotation-memory checks, and build coverage across all Mali-DP files are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.c

## Purpose

`malidp_hw.c` is the hardware abstraction layer for Mali-DP500, DP550, and DP650. It records per-variant layers, formats, register maps, IRQ maps, rotation-memory sizing, config-mode operations, timing programming, scaling coefficient programming, mclk validation, writeback programming, format/modifier mapping, and DE/SE IRQ handling.

## Important APIs, Types, And Functions

The file exports `malidp_device[]`, `malidp_format_modifiers[]`, `malidp_hw_get_format_id()`, `malidp_hw_format_is_linear_only()`, `malidp_hw_format_is_afbc_only()`, IRQ init/fini/hw-init helpers, and `malidp_format_get_bpp()`. Variant callbacks include `malidp500_*`, `malidp550_*`, and `malidp650_*` query, config-mode, modeset, rotmem, scaling, mclk, and memwrite functions. The internal memory-write state enum uses `MW_NOT_ENABLED`, `MW_ONESHOT`, `MW_START`, `MW_RESTART`, and `MW_STOP`.

## Control Flow

At bind time `malidp_drv.c` selects one `malidp_device[]` entry. `query_hw()` reads config registers to set min/max line size and rotation-memory banks. Modeset callbacks program output depth, background color, timing, sync polarities, interlace bit, prefetch start, and DP500 ARQOS workaround. Atomic checks call `rotmem_required()` and `se_calc_mclk()`. Commit paths call scaling coefficient callbacks and writeback enable/disable callbacks. DE IRQ handles DC config-valid completion first, sends pending events, updates the config-valid atomic, then handles vblank and error bits. SE IRQ handles scaling-engine/writeback completion and emulates one-shot writeback on DP500 by disabling memwrite after start.

## State And Persistence Behavior

The variant tables are static immutable driver data. Runtime hardware state lives in `struct malidp_hw_device`: line limits, rotation-memory sizes, output color depth, `pm_suspended`, `mw_state`, and ARQOS value. Hardware register state includes config-mode request, config-valid bit, timing, display function, scaling coefficients, memory-write pointers/strides, IRQ masks/status, and AFBC format IDs. IRQ handlers avoid MMIO when `pm_suspended` is true.

## Dependencies And Integration Points

This file depends on clocks, delays, MMIO, DRM FourCC/modifiers, vblank, Mali-DP register macros, driver private state, and writeback core. It is the central integration point between generic DRM state and variant-specific hardware programming for DP500/550/650.

## Risks And Edge Cases

Variant differences are dense: DP500 has a smaller address space, different config registers, no CLEARIRQ register, different scaling coefficient programming, one rotation-memory bank, and emulated writeback one-shot; DP550/650 share many paths but differ in line-size encodings, AFBC features, bus alignment, and rotation support. IRQ clearing differs by register-map feature. Some format IDs vary for AFBC YUYV. mclk checks only compare against current firmware-provided mclk. Memwrite state races are coordinated with config-valid IRQ state and must remain ordered.

## Test Signals

Validation should include DP500/550/650 probe, line-size and rotation-memory detection, mode timing programming, interlace programming, ARQOS on LS1028A-like systems, all supported format IDs and modifier variants, scaling coefficient changes, mclk rejection, writeback completion on DP500 and DP550/650, shared IRQ behavior while suspended, DE/SE error debugfs counters, and config-valid event wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.h

## Purpose

`malidp_hw.h` defines the Mali-DP hardware abstraction contract used by the rest of the driver. It describes block IDs, layer IDs, format IDs, IRQ maps, layer register metadata, scaling-engine configuration, register-map features, variant callback tables, runtime hardware-device state, MMIO helpers, IRQ helper prototypes, format helper prototypes, pitch-alignment/scaling helpers, and AFBC modifier constants.

## Important APIs, Types, And Functions

Key types include `struct malidp_format_id`, `struct malidp_irq_map`, `struct malidp_layer`, `struct malidp_se_config`, `struct malidp_hw_regmap`, `struct malidp_hw`, and `struct malidp_hw_device`. Inline helpers include `malidp_hw_read()`, `malidp_hw_write()`, `malidp_hw_setbits()`, `malidp_hw_clearbits()`, `malidp_get_block_base()`, IRQ enable/disable helpers, `malidp_hw_get_pitch_align()`, `malidp_se_select_coeffs()`, and `malidp_se_set_enh_coeffs()`.

## Control Flow

The header does not own top-level control flow but defines callback entry points used during probe, atomic check, commit, modeset, writeback, and IRQ setup. The `struct malidp_hw` callback table lets common DRM code call variant-specific `query_hw`, config-mode, modeset, rotation-memory, scaling, mclk, and memwrite functions without switch statements.

## State And Persistence Behavior

`struct malidp_hw_device` records mutable hardware runtime state: chosen variant, MMIO, APB/AXI/main/pixel clocks, min/max line sizes, output color depth, PM suspend flag, memory-write state, rotation-memory bank sizes, and ARQOS. Inline MMIO helpers warn on access while suspended but still perform the access. Scaling and AFBC constants define hardware programming values that persist in registers after writes.

## Dependencies And Integration Points

The header depends on bitops and `malidp_regs.h`, plus DRM AFBC modifier definitions available through included driver paths. It integrates all Mali-DP implementation files and exposes `malidp_device[]` and `malidp_format_modifiers[]` to the probe and plane/framebuffer validation paths.

## Risks And Edge Cases

The callback table is a hardware ABI inside the driver; a missing callback can break probe or commit paths. `malidp_hw_get_pitch_align()` increases alignment for rotated planes only on devices with bus alignments above 8 bytes. `malidp_se_select_coeffs()` uses fixed U16.16 threshold comparisons and must match coefficient table indexing. `malidp_se_set_enh_coeffs()` computes an offset differently depending on CLEARIRQ feature, so register-map feature flags must stay correct.

## Test Signals

Build coverage across all Mali-DP variants, runtime PM warnings for MMIO while suspended, pitch-alignment tests for rotated/unrotated DP650 planes, scaling coefficient selection boundaries, enhancer coefficient programming, IRQ enable/disable register writes, and format modifier enumeration are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.c

## Purpose

`malidp_mw.c` implements the Mali-DP writeback connector using the scaling engine memory-write path. It exposes an always-connected writeback connector, validates writeback framebuffer size/format/pitches, records DMA addresses in connector state, queues writeback jobs, and calls hardware `enable_memwrite` or `disable_memwrite` callbacks during atomic commit.

## Important APIs, Types, And Functions

The exported APIs are `malidp_mw_connector_init()` and `malidp_mw_atomic_commit()`. The private `struct malidp_mw_connector_state` extends connector state with up to two DMA addresses, pitches, internal format ID, plane count, and RGB-to-YUV coefficient tracking. `malidp_mw_encoder_atomic_check()` performs most validation. `get_writeback_formats()` builds a format list from hardware map entries that support `SE_MEMWRITE`.

## Control Flow

Connector initialization skips devices without `enable_memwrite`, attaches helper funcs, builds the writeback format list, and calls `drm_writeback_connector_init()` with the CRTC mask for the single CRTC. Atomic check ignores commits without a writeback job. With a job, it requires framebuffer dimensions to match the CRTC mode, rejects modifiers, maps the FourCC to a `SE_MEMWRITE` format ID, validates pitch alignment using non-rotated pitch rules, and records GEM DMA addresses plus offsets. Atomic commit queues the writeback job before programming hardware, optionally writes RGB-to-YUV coefficients for YUV targets once, and disables memwrite when no job is present.

## State And Persistence Behavior

Per-connector atomic state stores DMA programming values and whether RGB-to-YUV coefficients have already been initialized. Hardware writeback state is stored in `hwdev->mw_state` and handled in `malidp_hw.c` SE IRQs. Writeback job completion is signaled from SE IRQ completion paths, not directly here.

## Dependencies And Integration Points

The file depends on DRM writeback, DRM atomic helpers, GEM DMA framebuffer helpers, Mali-DP format mapping, pitch alignment, and hardware memwrite callbacks. It integrates with `malidp_drv.c` commit tail, which calls `malidp_mw_atomic_commit()` between plane commit and modeset enables, and with SE IRQ code that signals completion.

## Risks And Edge Cases

Writeback framebuffers must exactly match current mode dimensions; scaling into writeback is not supported here. Modifiers are rejected even if display planes support AFBC. Only up to two planes are recorded. The RGB-to-YUV initialization flag is carried across duplicated connector state; stale coefficients could matter if formats or colorimetry support expands. `malidp_mw_atomic_commit()` assumes `disable_memwrite` exists when connector state exists.

## Test Signals

IGT writeback tests, each advertised memory-write format, YUV writeback coefficient programming, invalid pitch rejection, modifier rejection, size mismatch rejection, job completion signaling on SE IRQ, repeated writeback jobs without repeated coefficient writes, and no-writeback disable commits are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.h

## Purpose

`malidp_mw.h` is the small internal header for Mali-DP memory-write/writeback support. It declares the connector initialization and atomic commit hooks used by the top-level driver.

## Important APIs, Types, And Functions

The two declarations are `malidp_mw_connector_init(struct drm_device *drm)` and `malidp_mw_atomic_commit(struct drm_device *drm, struct drm_atomic_state *old_state)`. The implementation-specific connector state and helpers remain private to `malidp_mw.c`.

## Control Flow

This header has no direct control flow. `malidp_drv.c` calls `malidp_mw_connector_init()` during mode-config initialization after CRTC setup. The custom atomic commit tail calls `malidp_mw_atomic_commit()` after display-plane register programming and before modeset enables/config-valid completion.

## State And Persistence Behavior

The header stores no state. It defines the cross-file contract through which writeback connector state and hardware memory-write state are managed by the implementation and the top-level commit path.

## Dependencies And Integration Points

The declarations require DRM device and atomic-state types from the including C files. The header integrates `malidp_drv.c` with `malidp_mw.c` and indirectly with hardware callbacks and SE IRQ completion logic.

## Risks And Edge Cases

Because this is the only public contract for writeback in the Mali-DP driver, signature or ordering changes must be coordinated with the commit tail. Passing `old_state` to `malidp_mw_atomic_commit()` is misleading because the implementation reads current connector state from `mw_conn->base.state`; future changes should preserve the current commit ordering assumptions.

## Test Signals

Build coverage with writeback enabled, connector creation on variants with `enable_memwrite`, and atomic commit tests with and without writeback jobs validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_mw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_planes.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_planes.c

## Purpose

`malidp_planes.c` implements Mali-DP display-engine plane creation, validation, atomic state management, modifier support, MMU prefetch selection, YUV color conversion programming, AFBC decoder programming, and plane register updates/disable.

## Important APIs, Types, And Functions

Exported APIs are `malidp_de_planes_init()` and `malidp_format_mod_supported()`. Important helpers include custom plane state reset/duplicate/destroy/print, `malidp_de_plane_check()`, `malidp_de_plane_update()`, `malidp_de_plane_disable()`, `malidp_se_check_scaling()`, prefetch helpers, `malidp_de_set_color_encoding()`, `malidp_de_set_plane_afbc()`, and `malidp_set_plane_base_addr()`.

## Control Flow

Plane initialization builds a per-layer format list from the hardware map, filters modifiers when SPLIT is unsupported, allocates one primary plane plus overlay planes, attaches helper funcs, creates alpha and blend-mode properties, adds rotation properties except on SMART layers, initializes alpha LUTs, and creates YUV color properties for video layers. Atomic check maps the framebuffer format/modifier to a hardware format ID, checks pitch/tile alignment, line-size limits, three-plane stride restrictions, scaling support, rotation restrictions, SMART AFBC rejection, rotation-memory requirement, alpha blending limitations, and MMU prefetch settings. Atomic update writes format, base addresses, MMU control, strides, color conversion, source/destination/offset sizes, SMART rectangle registers, AFBC crop/control, rotation/flip/blend/alpha/flow config, and finally enables the layer.

## State And Persistence Behavior

`struct malidp_plane_state` persists derived values: internal format ID, plane count, rotation memory size, MMU prefetch mode, and prefetch page size. CRTC state receives `scaled_planes_mask` for later scaling-engine setup. Hardware state persists in layer format/control/size/offset/stride/address/YUV2RGB/AFBC/MMU registers until another update or disable.

## Dependencies And Integration Points

The file depends on DRM atomic, blend, format/modifier helpers, GEM DMA helpers, IOMMU page-size information, Mali-DP hardware maps, CRTC state, and register definitions. It integrates tightly with `malidp_crtc.c` for scaling and rotation-memory budgeting and with `malidp_hw.c` for format IDs, pitch alignment, and AFBC feature support.

## Risks And Edge Cases

Modifier validation has many format-specific rules: AFBC requires one plane, RGB requires YTR, YUV forbids YTR, SPLIT requires SPARSE and is limited for subsampled formats, CBR requires subsampling, and some formats are linear-only or AFBC-only. Partial MMU prefetch is heuristic and depends on scatterlist lengths. AFBC base addressing ignores source crop because crop registers handle it. Hardware cannot combine plane alpha and pixel alpha. Rotation restrictions differ by layer and compression state.

## Test Signals

Coverage should include all layer types, every advertised format/modifier combination, invalid AFBC modifier combinations, pitch and tile-alignment failures, scaling on one plane and rejection on unsupported/multiple planes, rotation/flips on each layer, SMART layer restrictions, three-plane stride equality, YUV color property changes, MMU prefetch state printing, AFBC crop correctness, and disable clearing enable/flow bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_planes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_regs.h

## Purpose

`malidp_regs.h` is the register and bitfield definition header for Mali-DP500/DP550/DP650. It names interrupt bits, common display/scaling/memwrite fields, generic IRQ register offsets, timing-register offsets and pack macros, coefficient table registers, scaling-engine registers, memory-write registers, DP500-specific offsets, DP550/650 offsets, MMU control bits, and AFBC decoder registers.

## Important APIs, Types, And Macros

Important groups include `MALIDP*_DE_IRQ_*`, `MALIDP*_SE_IRQ_*`, `MALIDP*_DC_IRQ_*`, `MALIDP_CFG_VALID`, `MALIDP_DISP_FUNC_*`, `MALIDP_SCALE_ENGINE_EN`, `MALIDP_SE_MEMWRITE_EN`, `MALIDP_REG_STATUS/SETIRQ/MASKIRQ/CLEARIRQ`, timing pack macros such as `MALIDP_DE_H_FRONTPORCH()`, coefficient offsets, `MALIDP_SE_*` scaling/enhancer macros, `MALIDP_MW_*` registers, DP500/550 config/timing/layer/memwrite bases, `MALIDP_MMU_CTRL_*`, and AFBC decoder macros such as `MALIDP_AD_EN`, `MALIDP_AD_YTR`, and `MALIDP_AD_BS`.

## Control Flow

The header has no executable control flow. Driver code uses its constants to program variant-specific register maps through the callback tables in `malidp_hw.c`, plane programming in `malidp_planes.c`, writeback programming in `malidp_mw.c`, and commit/color/scaling programming in `malidp_drv.c`.

## State And Persistence Behavior

No software state is stored here. The macros describe hardware register state that persists in the display processor: IRQ masks/status, config-valid/mode bits, timing values, output depth, background color, coefficient tables, scaling state, memwrite DMA pointers, MMU prefetch control, and AFBC decoder state.

## Dependencies And Integration Points

The file depends only on C macros and bit definitions. It is consumed by `malidp_hw.h` and all Mali-DP implementation files. It encodes the differences between DP500's mixed register layout and the standardized DP550/650 layout.

## Risks And Edge Cases

DP500 and DP550/650 offsets are not interchangeable. Some registers are relative to block bases, while others are absolute variant offsets. IRQ clearing differs based on CLEARIRQ support outside this header. Timing macros mask values, so out-of-range values can be truncated unless earlier validation catches them. MMU prefetch page-size bits and AFBC crop/control bits must match format/modifier validation.

## Test Signals

Hardware smoke tests for each variant, register dumps before/after modeset, IRQ mask/status behavior, scaling/memwrite/AFBC functionality, interlaced timing programming, MMU prefetch tests, and static comparison against ARM register documentation are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Kconfig

## Purpose

`armada/Kconfig` declares the `DRM_ARMADA` kernel configuration option for Marvell Armada SoC LCD controller DRM support.

## Important APIs, Types, And Functions

The config symbol is `DRM_ARMADA`, a tristate labeled "DRM support for Marvell Armada SoCs". It depends on `DRM`, `HAVE_CLK`, `ARM`, and `MMU`. It selects `DRM_CLIENT_SELECTION`, `DRM_KMS_HELPER`, and conditionally `FB_IOMEM_HELPERS` when `DRM_FBDEV_EMULATION` is enabled.

## Control Flow

Kconfig has no runtime control flow. Build selection controls whether the Armada DRM module is built in, built as a module, or omitted. Selected helper symbols ensure the driver has KMS and fbdev helper support needed by the Makefile-selected objects.

## State And Persistence Behavior

No runtime state is stored here. Build-time state determines object compilation, module availability, and whether fbdev helper code can use I/O-memory fb operations.

## Dependencies And Integration Points

This file integrates the Armada driver with the kernel DRM build system. The help text documents support for Armada 510 LCD controllers, graphics/video overlays, KMS, and userspace buffer management without built-in acceleration.

## Risks And Edge Cases

The `ARM && MMU` dependency excludes other architectures or no-MMU builds even if code compiles. Selecting `DRM_CLIENT_SELECTION` affects DRM client behavior. If fbdev emulation is enabled without `FB_IOMEM_HELPERS`, the fbdev object would miss required helper ops, hence the conditional select.

## Test Signals

Build tests should cover `DRM_ARMADA=m`, `DRM_ARMADA=y`, fbdev emulation on/off, and dependency-disabled configurations. Runtime probe tests validate the config actually produces `armada-drm`/`armada-lcd` platform driver registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Makefile

## Purpose

`armada/Makefile` defines how the Armada DRM driver objects are built and linked into `armada.o`.

## Important APIs, Types, And Functions

The base `armada-y` object list includes `armada_crtc.o`, `armada_drv.o`, `armada_fb.o`, `armada_gem.o`, `armada_overlay.o`, `armada_plane.o`, `armada_trace.o`, and `armada_510.o`. Conditional additions are `armada_debugfs.o` for `CONFIG_DEBUG_FS` and `armada_fbdev.o` for `CONFIG_DRM_FBDEV_EMULATION`. `obj-$(CONFIG_DRM_ARMADA) := armada.o` connects the aggregate to Kconfig.

## Control Flow

There is no runtime control flow. The build system concatenates the object list into one module/built-in object according to the selected kernel configuration.

## State And Persistence Behavior

No runtime state is stored. Build-time state controls whether debugfs and fbdev support are present in the final driver.

## Dependencies And Integration Points

The Makefile integrates with `Kconfig`, the DRM subsystem build, and local Armada source files. The inclusion of `armada_trace.o` ensures tracepoints are linked when the driver is built.

## Risks And Edge Cases

Object ordering can matter for init/exit references and tracepoint definitions. Conditional object omissions must match preprocessor guards in headers and driver ops. Adding a new local file without updating `armada-y` silently excludes it from the driver.

## Test Signals

Build tests with debugfs and fbdev combinations, module link checks, unresolved symbol scans, and verifying `modinfo`/module contents for expected objects are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_510.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_510.c

## Purpose

`armada_510.c` implements Armada 510/Dove variant-specific CRTC support. It discovers variant clocks, initializes SPU hardware defaults, selects a pixel clock source/divider, and provides enable/disable hooks for the generic Armada CRTC code.

## Important APIs, Types, And Functions

The exported object is `armada510_ops`, a `struct armada_variant`. Private state is `struct armada510_variant_data`, storing up to four clocks and the selected clock. Important functions are `armada510_crtc_init()`, `armada510_crtc_compute_clock()`, `armada510_crtc_disable()`, and `armada510_crtc_enable()`. `armada510_clocking` defines HDMI clock tolerance and divider limits.

## Control Flow

CRTC creation calls `init()`, which allocates variant state, obtains clocks by DT `clock-names` or a legacy `ext_ref_clk1`, lowers the DMA watermark, disables SRAM wait state, and initializes the SPU advanced hardware cursor/blend register. Mode fixup calls `compute_clock()` with `sclk == NULL` to validate support. Mode setting calls it again with an output pointer, which enables a candidate clock, optionally sets rate and SCLK selector/divider, stores the selected clock, swaps the active CRTC clock, and disables the temporary reference. Enable prepares the selected clock if not already active; disable unprepares the active clock.

## State And Persistence Behavior

`variant_data` persists per CRTC and stores discovered clocks plus `sel_clk`. `dcrtc->clk` tracks the currently prepared clock. SPU register initialization persists until later register writes or reset. The selected SCLK register value is queued by generic mode-setting code and written to hardware.

## Dependencies And Integration Points

The file depends on Linux clk and OF helpers, Armada CRTC/private/hardware headers, and generic `armada_crtc_select_clock()`. It is referenced by the LCD platform match table for `marvell,dove-lcd` and platform IDs.

## Risks And Edge Cases

Clock discovery returns `-EPROBE_DEFER` for missing named clocks. `strnstr` is not involved here; matching is by exact clock-name strings. `clk_prepare_enable()` is used during clock computation and must be balanced. The compute function assumes setting the selected clock in the second call cannot fail in a way not seen during validation. The SRAM wait-state/watermark workaround is variant-specific and could affect bandwidth stability.

## Test Signals

Tests should cover DT clock-name permutations, legacy non-DT clock path, mode validation around HDMI tolerance limits, SCLK selector programming for each source, clock enable/disable across modesets and DPMS, high-bandwidth jitter regressions, and probe deferral when clocks are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.c

## Purpose

`armada_crtc.c` implements the Marvell Armada LCD CRTC component driver. It handles register-queue updates, timing programming including interlaced-field fixups, IRQ/vblank/event handling, gamma SRAM programming, hardware cursor management, clock selection support, CRTC creation/destruction, and LCD component/platform driver registration.

## Important APIs, Types, And Functions

Exported APIs are `armada_drm_crtc_update_regs()`, `armada_crtc_select_clock()`, and `armada_lcd_platform_driver`. Major internal functions include `armada_drm_crtc_mode_set_nofb()`, atomic check/begin/flush/enable/disable helpers, IRQ helpers, cursor set/move/update/load helpers, `armada_drm_crtc_create()`, and component bind/unbind/probe routines. `struct armada_regs` queues masked register writes used by atomic plane/CRTC paths.

## Control Flow

LCD platform probe registers a component. Bind maps MMIO, allocates `struct armada_crtc`, initializes registers and IRQ state, requests the IRQ, runs variant init, creates the primary plane and CRTC, enables color management, and creates overlay planes. Mode fixup validates mode flags and asks the variant to validate clocking. Mode-set computes real SCLK, prepares per-field interlaced timing values, queues timing/polarity registers, and writes them under `irq_lock`. Atomic begin handles gamma changes and starts a register queue. Atomic flush terminates the queue and either applies immediately for modesets or defers to `DUMB_FRAMEDONE` IRQ for active updates, arming events as needed. IRQ handles underflows, vblank, interlaced field register swaps, deferred register application, cursor updates, and event delivery.

## State And Persistence Behavior

`struct armada_crtc` stores CRTC number, MMIO base, selected clock, interlace field register snapshots, cursor object/position/size, dumb/io-pad config, IRQ enable mask, pending update/event flags, and atomic register queue. Hardware state persists in LCD SPU timing, DMA, SRAM, cursor, IRQ, and clock registers. Cursor GEM objects can call back into `cursor_update()` after CPU writes.

## Dependencies And Integration Points

The file depends on DRM atomic/vblank helpers, component framework, OF/platform matching, Armada fb/GEM/plane/overlay/hardware headers, tracepoints, and variant callbacks from `armada_510.c`. It integrates with `armada_drv.c` as a child component bound into the master DRM device.

## Risks And Edge Cases

Interlaced modes require per-field register rewrites on graphics frame IRQs and an extra vblank reference. Deferred register queues have a fixed 32-entry array; plane code must not overflow it. Event delivery waits until updates are no longer pending. Cursor SRAM has unusual ABGR packing and size limits. IRQ enable/disable is protected by `irq_lock`, and incorrect masking can lose vblank or frame-done events. Mode validation rejects vscan/doublescan/hskew and interlace without advanced register support.

## Test Signals

Validation should cover progressive and interlaced modes, frame-done deferred updates, vblank/page-flip events, gamma LUT size and SRAM programming, cursor set/move/cropping/reload, underflow logging, clock selection boundaries, component bind/unbind, overlay/primary plane register queue interactions, and debugfs register visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.h

## Purpose

`armada_crtc.h` defines the Armada CRTC private structure, register-queue helpers, clock-selection data structures, and CRTC/platform-driver declarations shared by Armada DRM files.

## Important APIs, Types, And Functions

`struct armada_regs` stores one queued register update as offset, mask, and value. Macros `armada_reg_queue_mod()`, `armada_reg_queue_set()`, and `armada_reg_queue_end()` append queue entries and terminators. `struct armada_crtc` embeds `struct drm_crtc` and stores variant data, MMIO, clock, interlaced field values, cursor state, hardware config, IRQ state, deferred update/event state, and a 32-entry register queue. `struct armada_clocking_params` and `struct armada_clk_result` support clock selection. The header declares `armada_drm_crtc_update_regs()`, `armada_crtc_select_clock()`, and `armada_lcd_platform_driver`.

## Control Flow

The header has no standalone control flow. Register-queue macros are used by CRTC and plane atomic code to batch masked writes. The `armada_crtc` fields are read and mutated by CRTC IRQ, atomic, cursor, debugfs, and variant code.

## State And Persistence Behavior

The struct defines persistent per-CRTC software state, especially deferred register updates and cursor/update flags that bridge atomic commit code and IRQ handling. `atomic_regs` is stack-like per-commit state stored in the CRTC object. `event` persists until vblank delivery.

## Dependencies And Integration Points

The header depends on DRM CRTC types and forwards Armada GEM/variant types. It integrates `armada_crtc.c`, variant files, plane/overlay code, debugfs, and master driver code.

## Risks And Edge Cases

The queue macros do not bounds-check `regs_idx`; callers must ensure the 32-entry array is sufficient. The mask convention stores the inverted mask in queue entries, so misuse can write unexpected bits. `drm_to_armada_crtc()` assumes the embedded CRTC layout. Cursor object references and update callbacks must be cleared before object release.

## Test Signals

Compile coverage, register queue overflow review, atomic plane update tests that use queued registers, IRQ/event tests, cursor lifetime tests, and clock-selection unit-style coverage are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_crtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_debugfs.c

## Purpose

`armada_debugfs.c` implements debugfs support for the Armada DRM driver. It exposes the global linear GEM memory allocator state and per-CRTC LCD register dumps/masked writes.

## Important APIs, Types, And Functions

The exported functions are `armada_drm_crtc_debugfs_init()` and `armada_drm_debugfs_init()`. `armada_debugfs_gem_linear_show()` prints `priv->linear` through `drm_mm_print()`. `armada_debugfs_crtc_reg_show()` dumps registers from offsets `0x84` through `0x1c4`. `armada_debugfs_crtc_reg_write()` parses `reg mask val`, validates range/alignment, and applies a masked register write.

## Control Flow

The driver-level debugfs init creates a DRM info file named `gem_linear`. Each CRTC late-register hook creates `armada-regs` under the CRTC debugfs entry. Reads walk allocator/register state. Writes to `armada-regs` are accepted only at offset zero, truncated to a small stack buffer, parsed, range-checked, then applied directly to MMIO.

## State And Persistence Behavior

Debugfs reads do not mutate state except for normal locking. Writes mutate live hardware registers and persist until later driver writes or reset. `gem_linear` output reflects the current `drm_mm` allocator protected by `linear_lock`.

## Dependencies And Integration Points

The file depends on debugfs, seq_file, uaccess, DRM debugfs helpers, Armada private state, and CRTC MMIO. It is conditionally built by the Makefile under `CONFIG_DEBUG_FS` and called from the master and CRTC registration paths.

## Risks And Edge Cases

The register write interface is powerful and bypasses normal driver validation; it is root/debugfs-only but can disrupt active scanout. Only a fixed register range is exposed. Parsing uses `%lx` values and does not accept symbolic names. Direct MMIO writes are not synchronized with all atomic paths except no explicit locks here.

## Test Signals

Validation includes debugfs presence under `CONFIG_DEBUG_FS`, absence when disabled, `gem_linear` consistency during GEM allocate/free, register dump readability, invalid write rejection, valid masked write behavior, and no crashes during concurrent modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drm.h

## Purpose

`armada_drm.h` defines shared private structures, helpers, variant operations, fbdev hooks, and debugfs declarations for the Armada DRM driver.

## Important APIs, Types, And Functions

Inline helpers include `armada_updatel()` for read/modify/write MMIO updates and `armada_pitch()` for 128-byte-aligned scanout pitch calculation. `struct armada_variant` defines per-variant `init`, `compute_clock`, `disable`, and `enable` callbacks. `struct armada_private` embeds `struct drm_device`, stores up to two CRTC pointers, a `drm_mm` linear allocator protected by `linear_lock`, shared plane property pointers, and debugfs root. The header declares `armada510_ops`, overlay creation, fbdev probe hook, and debugfs init functions.

## Control Flow

The header has no top-level control flow. Its helpers are called during framebuffer/dumb allocation, CRTC setup, variant programming, and register updates. Conditional macros provide fbdev driver ops only when fbdev emulation is configured.

## State And Persistence Behavior

`struct armada_private` defines the master DRM device state, especially the linear graphics-memory allocator used by GEM and the CRTC array used by components. Variant callbacks persist in each CRTC. `armada_updatel()` mutates hardware registers only when the value changes. `armada_pitch()` provides persistent ABI-visible pitch values returned to dumb-buffer callers.

## Dependencies And Integration Points

The header depends on Linux kfifo/io/workqueue includes, DRM device/mm/fb helper types, and local CRTC/GEM declarations. It integrates `armada_drv.c`, CRTC, GEM, framebuffer, fbdev, overlay, plane, and debugfs code.

## Risks And Edge Cases

`armada_pitch()` has special handling for 4bpp and aligns every pitch to 128 bytes; changing it affects userspace buffer layouts. `armada_updatel()` uses relaxed MMIO and no locking; callers must provide ordering and serialization. Conditional fbdev ops must remain synchronized with Makefile object selection.

## Test Signals

Build coverage with fbdev/debugfs enabled and disabled, dumb-buffer pitch tests for multiple bpp values, GEM allocator lockdep, register-update behavior, and probe with one or two CRTCs validate this shared contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drv.c

## Purpose

`armada_drv.c` is the Armada DRM master platform driver. It registers DRM ioctls, allocates the master DRM device, initializes mode-config and linear graphics-memory management, binds LCD CRTC components, initializes vblank/polling/debugfs/client setup, and registers both master and LCD platform drivers at module init.

## Important APIs, Types, And Functions

Key objects are `armada_ioctls`, `armada_drm_driver`, `armada_drm_mode_config_funcs`, `armada_master_ops`, `armada_drm_platform_driver`, and module init/exit functions. Important functions include `armada_drm_bind()`, `armada_drm_unbind()`, `armada_add_endpoints()`, `armada_drm_probe()`, `armada_drm_remove()`, and `armada_drm_shutdown()`.

## Control Flow

Module init first checks `drm_firmware_drivers_only()`, then registers the LCD platform driver and the master DRM platform driver. Master probe prefers `drm_of_component_probe()` and falls back to platform-data component matching plus endpoint matching. Bind scans platform memory resources, expecting resources above 64 KiB to be graphics memory and smaller resources to be invalid for the master, reserves the memory region, allocates `struct armada_private`, removes conflicting aperture devices, initializes mode-config limits, initializes the `drm_mm` linear allocator, binds components, initializes vblank, resets mode config, starts polling, registers the DRM device, initializes debugfs, and starts DRM client setup. Unbind reverses polling, unregister, atomic shutdown, component unbind, mode-config cleanup, allocator teardown, and drvdata clearing.

## State And Persistence Behavior

Persistent master state is `struct armada_private`, especially the DRM device, CRTC pointers, and linear allocator over the graphics memory resource. Userspace-visible ioctls include GEM create, mmap, and pwrite. The platform drivers remain registered until module exit.

## Dependencies And Integration Points

This file integrates Linux platform/component/OF graph infrastructure, aperture removal, DRM core/ioctls/PRIME helpers, Armada GEM/fb/CRTC/overlay code, and fbdev/debugfs optional paths. It binds child LCD components provided by `armada_crtc.c`.

## Risks And Edge Cases

Memory resource scanning treats any resource <=64 KiB as an error in the master path, so DT/platform resource ordering matters. Component matching has OF and legacy platform-data paths. Error unwinding must clean mode-config and `drm_mm` only after initialization. Debugfs init is called after `drm_dev_register()` using the primary minor. The driver exposes custom ioctls, so ABI compatibility matters.

## Test Signals

Tests include module load/unload, OF component probe and legacy platform-data probe, graphics-memory resource validation, aperture takeover, one/two LCD component binding, vblank init, DRM ioctl smoke tests, dumb-buffer creation, debugfs creation, fbdev client setup, shutdown behavior, and error injection for component bind/register failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.c

## Purpose

`armada_fb.c` implements Armada framebuffer object creation and maps DRM FourCC formats to Armada LCD hardware format/config bits.

## Important APIs, Types, And Functions

The exported functions are `armada_framebuffer_create()` and `armada_fb_create()`. `armada_fb_funcs` delegates destroy and handle creation to GEM framebuffer helpers. `armada_framebuffer_create()` fills `struct armada_framebuffer` with hardware `fmt` and `mod` values and initializes the DRM framebuffer. `armada_fb_create()` is the mode-config framebuffer creation callback.

## Control Flow

Framebuffer creation maps `mode->pixel_format` through a switch covering RGB, BGR, ARGB/ABGR, packed and planar YUV, and C8 formats. It allocates an Armada framebuffer wrapper, stores the GEM object in `fb.obj[0]`, fills DRM framebuffer fields, initializes the framebuffer, and takes a GEM reference for framebuffer lifetime. The user-facing create callback logs the request, requires all planes to use the same handle for multi-plane formats, looks up the GEM object, maps imported objects if needed, rejects objects without a scanout device address, delegates wrapper creation, and drops the lookup reference.

## State And Persistence Behavior

`struct armada_framebuffer` persists as a DRM framebuffer and stores hardware format/modifier config used by plane programming. It owns a reference on the underlying GEM object. No hardware registers are written here; state is consumed later by plane/CRTC code.

## Dependencies And Integration Points

The file depends on DRM framebuffer/GEM helper APIs, Armada GEM lookup/import mapping, Armada hardware format bits, and `struct armada_framebuffer` from `armada_fb.h`. It is registered via `armada_drm_mode_config_funcs` in `armada_drv.c`.

## Risks And Edge Cases

The implementation only handles single-handle multi-plane framebuffers, which restricts planar YUV layouts. Imported buffers must map to one contiguous DMA segment through `armada_gem_map_import()`. A framebuffer requires `obj->mapped` so it can be scanned out. Format mapping must remain synchronized with plane register programming and userspace expectations.

## Test Signals

Validation includes framebuffer creation for every supported FourCC, rejection of unsupported formats, multi-handle multi-plane rejection, imported contiguous dmabuf success and scattered import rejection, GEM reference lifetime tests, and scanout tests verifying channel order and YUV swap bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.h

## Purpose

`armada_fb.h` declares the Armada framebuffer wrapper and framebuffer creation APIs shared by the DRM master, fbdev, and plane code.

## Important APIs, Types, And Functions

`struct armada_framebuffer` embeds `struct drm_framebuffer` and adds 8-bit hardware `fmt` and `mod` fields. `drm_fb_to_armada_fb()` converts from DRM framebuffer to wrapper. `drm_fb_obj()` obtains the first GEM object as an Armada GEM object. The header declares `armada_framebuffer_create()` and `armada_fb_create()`.

## Control Flow

The header itself has no control flow. Its conversion helpers are used by framebuffer and plane paths to access hardware format state and backing GEM objects. Creation functions are implemented in `armada_fb.c` and called from mode-config and fbdev setup.

## State And Persistence Behavior

The wrapper stores persistent per-framebuffer hardware format metadata derived at creation time. It does not own allocation state directly beyond the embedded DRM framebuffer's GEM references.

## Dependencies And Integration Points

The header depends on DRM framebuffer types and local Armada GEM declarations through including code. It connects `armada_fb.c`, `armada_fbdev.c`, and scanout/plane code.

## Risks And Edge Cases

The `drm_fb_obj()` macro assumes the first object is an Armada GEM object and that all relevant planes share that object. This matches current framebuffer creation restrictions but would need revision for true multi-object planar buffers.

## Test Signals

Compile coverage, framebuffer creation tests, plane scanout using `fmt`/`mod`, and fbdev setup validate this small contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fbdev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fbdev.c

## Purpose

`armada_fbdev.c` implements fbdev emulation backing for the Armada DRM driver when `CONFIG_DRM_FBDEV_EMULATION` is enabled. It allocates a private linear GEM buffer, maps it for CPU access, wraps it in an Armada framebuffer, and initializes `fb_info`.

## Important APIs, Types, And Functions

The exported function is `armada_fbdev_driver_fbdev_probe()`, referenced through `ARMADA_FBDEV_DRIVER_OPS`. `armada_fb_ops` combines `FB_DEFAULT_IOMEM_OPS`, DRM fb helper ops, and a custom destroy hook. `armada_fbdev_fb_destroy()` finalizes the helper, destroys the framebuffer, and releases the DRM client.

## Control Flow

Fbdev probe builds a `drm_mode_fb_cmd2` from requested surface size/depth/bpp, computes pitch with `armada_pitch()`, allocates a private GEM object, backs it from linear memory, maps it with `armada_gem_map_object()`, creates an Armada framebuffer, drops the initial GEM reference, sets fbops and screen memory fields, stores helper callbacks/framebuffer, fills fb_info, and logs allocation details. Error paths drop GEM references on failed backing or mapping.

## State And Persistence Behavior

The fbdev buffer is a private, linear-backed GEM object with CPU mapping in `obj->addr`. `fb_info` stores physical start, length, screen size, and screen base. The framebuffer holds the long-lived reference after creation. Destroy tears down the fb helper, framebuffer, and client.

## Dependencies And Integration Points

The file depends on Linux fb APIs, DRM fb helper/client infrastructure, Armada pitch, GEM allocation/backing/mapping, and Armada framebuffer creation. It is conditionally compiled by the Makefile and exposed through driver ops in `armada_drm.h`.

## Risks And Edge Cases

The fbdev path requires contiguous linear graphics memory and a successful WC mapping. `armada_framebuffer_create()` may fail after GEM mapping; the code drops the initial GEM reference and relies on framebuffer lifetime only on success. The helper uses I/O-memory fb ops, so `FB_IOMEM_HELPERS` must be selected.

## Test Signals

Boot console/fbdev smoke tests, fbdev emulation enabled/disabled builds, framebuffer allocation at common depths, mmap/write/read through fbdev, cleanup on unregister, and memory-leak/refcount checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_fbdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.c

## Purpose

`armada_gem.c` implements Armada GEM buffer allocation, backing, CPU mapping, dumb buffers, private GEM ioctls, pwrite updates, mmap for shmem-backed objects, PRIME export/import, and scanout mapping of imported buffers. It supports page-backed small objects, contiguous linear graphics-memory objects, shmem objects, and imported dma-bufs.

## Important APIs, Types, And Functions

Exported APIs include `armada_gem_free_object()`, `armada_gem_linear_back()`, `armada_gem_map_object()`, `armada_gem_alloc_private_object()`, `armada_gem_dumb_create()`, `armada_gem_create_ioctl()`, `armada_gem_mmap_ioctl()`, `armada_gem_pwrite_ioctl()`, `armada_gem_prime_export()`, `armada_gem_prime_import()`, and `armada_gem_map_import()`. The file defines `armada_gem_vm_ops`, object funcs, and custom dma-buf ops for PRIME export.

## Control Flow

Private objects are initialized without shmem; normal GEM create ioctl initializes shmem-backed GEM. Dumb create computes aligned pitch/size, allocates a private object, backs it with `armada_gem_linear_back()`, creates a handle, and drops the allocation reference. Linear backing uses small page allocations for <=8192-byte CPU-only objects, otherwise allocates from the master `drm_mm`, clears the WC mapping, and records physical/device addresses. Mapping ioremaps linear objects. Pwrite validates user memory, looks up a kernel-mapped object, bounds-checks offset/size, copies data, and calls an optional update callback, used by cursor updates. PRIME export maps shmem/page/linear objects into sg tables; import attaches a dma-buf lazily and `armada_gem_map_import()` later maps it for scanout, requiring one sufficiently large DMA segment.

## State And Persistence Behavior

`struct armada_gem_object` stores address, physical address, device address, mapped flag, linear drm_mm node, small backing page, imported sg table, and optional update callback. Linear allocator state persists in `priv->linear` under `linear_lock`. Imported attachments persist until object free, where mapped attachments are unmapped and PRIME state destroyed.

## Dependencies And Integration Points

The file depends on dma-buf, DMA mapping, shmem, DRM PRIME/GEM helpers, Armada custom uAPI structs, private driver state, and GEM header definitions. It integrates with framebuffer creation, fbdev allocation, cursor upload/update, dumb-buffer ABI, and PRIME sharing.

## Risks And Edge Cases

`armada_gem_pwrite_ioctl()` returns `-EINVAL` without dropping the GEM reference if `!dobj->addr`, which is a leak risk in that path. Imported dmabufs with multiple sg entries or short DMA length are rejected but the failure path leaves `dobj->sgt` set after `armada_gem_map_import()` errors, so callers/free paths must handle it carefully. Linear objects use physical addresses and WC ioremap rather than DMA coherent allocation by design. PRIME mmap is disabled. Small page-backed objects are CPU accessible but not marked mapped for scanout.

## Test Signals

Tests should cover dumb create/pitch/handle lifecycle, private GEM create/mmap/pwrite, cursor pwrite update callback, linear allocator exhaustion/free, small cursor object allocation, fbdev mapping, PRIME export/import self-import and foreign import, scattered import rejection, object free leak checks, mmap fault insertion for linear objects, and refcount/error-path testing around pwrite and import failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.h

## Purpose

`armada_gem.h` defines the Armada GEM object wrapper and declarations for GEM allocation, backing, mapping, dumb-buffer, PRIME, import, and lookup helpers.

## Important APIs, Types, And Functions

`struct armada_gem_object` embeds `struct drm_gem_object` and stores CPU address, physical address, device address, mapped flag, linear allocator node, small backing page, imported sg table, and an update callback/data pointer. `drm_to_armada_gem()` converts from base GEM object. Declarations cover free, linear backing, CPU mapping, private allocation, dumb create, PRIME export/import, import mapping, and `armada_gem_object_lookup()`.

## Control Flow

The header itself has no runtime control flow. `armada_gem_object_lookup()` calls `drm_gem_object_lookup()` and converts the result to the Armada wrapper. Other functions are implemented in `armada_gem.c` and called by framebuffer, fbdev, cursor, ioctl, and PRIME paths.

## State And Persistence Behavior

The struct defines all persistent per-buffer backing state. `addr` indicates CPU accessibility, `phys_addr`/`dev_addr` support MMIO scanout and mmap fault insertion, `mapped` gates scanout framebuffer creation, `linear`/`page`/`sgt` identify backing type, and `update` allows CPU writes to trigger hardware cursor reloads.

## Dependencies And Integration Points

The header depends on DRM GEM types and is included by Armada CRTC, framebuffer, fbdev, and driver code. It integrates custom GEM ioctls with core DRM GEM handles and PRIME.

## Risks And Edge Cases

Consumers must respect backing-type invariants: not every object has `addr`, not every object is scanout-mapped, and imported objects need explicit mapping before framebuffer use. The update callback pointer must be cleared before cursor object release to avoid use-after-free callbacks.

## Test Signals

Compile coverage, GEM handle lookup tests, cursor object lifetime tests, imported object scanout mapping, dumb-buffer creation, and object free coverage for page/linear/imported cases validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/armada/armada_gem.h -->
