# subset-b-003750 Tegra DRM Display Controller, DP, DPAUX, DRM Core, and DSI Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.c

## Purpose
`dc.c` implements the Tegra display-controller host1x client and DRM CRTC/plane backend. It translates DRM atomic CRTC and plane state into Tegra display-controller register programming for legacy display controllers and NVdisplay generations. It also owns DC runtime power sequencing, VBLANK handling, debugfs visibility, SoC capability tables, RGB output attachment, display bandwidth programming, and host1x syncpoint integration.

## Important APIs, Types, and Functions
The public entry points exported through `dc.h` are `tegra_dc_has_output()`, `tegra_dc_commit()`, `tegra_dc_state_setup_clock()`, and `tegra_crtc_atomic_post_commit()`. The host1x client callbacks are grouped in `dc_client_ops`: early init increments `tegra->num_crtcs`, init creates planes/CRTC/output/IRQ state, exit tears them down, late exit decrements the count, and suspend/resume drive reset, clocks, powergate, and runtime PM.

Plane handling is centered on `tegra_plane_atomic_check()`, `tegra_plane_atomic_update()`, `tegra_plane_atomic_disable()`, and `tegra_dc_setup_window()`. Cursor-specific behavior is split into `tegra_cursor_atomic_check()`, `__tegra_cursor_atomic_update()`, async cursor update hooks, and cursor plane creation. CRTC behavior is in `tegra_crtc_atomic_enable()`, `tegra_crtc_atomic_disable()`, `tegra_crtc_atomic_begin()`, `tegra_crtc_atomic_flush()`, and `tegra_crtc_atomic_check()`.

## Control Flow
Probe coerces the device DMA mask to match host1x, allocates `struct tegra_dc`, parses the pipe/head, handles Tegra20 DC coupling, acquires clocks/resets, forces the controller into reset, powers off legacy powergates, initializes OPP support, maps registers, probes RGB output, enables runtime PM, and registers as a host1x client. During host1x initialization, the driver allocates a syncpoint, attaches to the IOMMU, creates primary/overlay/cursor/shared planes depending on SoC data, initializes the CRTC, initializes RGB output, requests the IRQ, and inherits DMA parameters from host1x.

Atomic plane check validates pixel format, tiling, rotation/reflection, legacy blending state, and multi-plane UV stride constraints, then adds the plane to the DC state for update-bit tracking. Atomic update builds a `tegra_dc_window` from DRM coordinates, framebuffer offsets, IOVA addresses, tiling, format, byte swap, zpos, and reflection, then calls `tegra_dc_setup_window()`. That routine programs color depth, destination and source geometry, DDA scaling increments, base addresses, line strides, tiling/surface kind, CSC defaults, filtering coefficients, direction bits, and legacy or modern blending registers.

CRTC enable applies the selected parent clock and pixel clock, resumes the host1x client, configures syncpoint VBLANK counters, interrupt type/polarity/mask state, background/border color, shift clock divider, display timings, interlace disable, display command mode, legacy power rails, NVdisplay underflow reporting, optional RGB clock qualifiers, commits state, and turns VBLANK on. Disable stops the controller, handles RGB-specific power-control bits, resets per-period stats, turns VBLANK off, sends pending events, suspends the host1x client, and clears OPP performance state.

## State and Persistence
Persistent driver state is stored in `struct tegra_dc`: mapped registers, pipe id, clock/reset/powergate handles, syncpoint, RGB output, stats counters, debugfs file array, SoC info, and OPP availability. Per-CRTC state is in `struct tegra_dc_state`, which persists selected clock parent, pixel clock, divider, and plane update bits across atomic check/commit. Runtime register state is explicitly double/triple buffered; `tegra_dc_commit()` writes update/activate request bits so assembly state becomes active at stop mode or frame boundary. Stats have current-period and total counters; current counters reset on CRTC disable while totals persist for the device lifetime.

## Dependencies and Integration Points
The file integrates with DRM atomic helpers, DRM plane and CRTC objects, host1x client/syncpoint/channel infrastructure, Tegra GEM/framebuffer helpers, `plane.c` state helpers, display hub support for NVdisplay shared planes, Tegra RGB output code, runtime PM, reset, clocks, powergates, OPP/genpd, interconnect bandwidth, debugfs, and device tree bindings such as `nvidia,head` and `nvidia,outputs`. It relies on `dc.h` for register definitions and on SoC capability tables in this file to select formats, modifiers, cursor support, powergate behavior, and NVdisplay/shared-window behavior.

## Risks
This file is highly hardware-sensitive. Register write ordering and update/activate bit selection can produce blank displays, stuck commits, or tearing. Bandwidth calculations only handle the legacy maximum-three-plane assumption and intentionally bypass NVdisplay. Legacy blending is complex and tied to normalized zpos and alpha/opaque inference. The code contains known assumptions around DT node ordering for `nvidia,head`, Tegra20 coupled PM, RGB/DC coupling during disable, and symmetric DSI ganged modes in the caller. Async cursor updates directly poke hardware and must preserve existing framebuffer/size visibility constraints. Error cleanup around partially created planes uses cleanup paths that must match plane allocation ownership.

## Test Signals
Useful signals include successful DRM device registration with expected CRTC count, modeset enable/disable without timeout in `tegra_dc_wait_idle()`, stable VBLANK counts from syncpoint or DRM fallback, clean debugfs `regs`, `crc`, and `stats` reads while active, no underflow/overflow increments under common plane compositions, correct plane format/modifier rejection, cursor async movement without full modeset, runtime suspend/resume cycles, HDMI/RGB/DSI/SOR modesets across supported SoCs, and interconnect bandwidth transitions that rise before commit and drop only after post-commit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.h

## Purpose
`dc.h` is the shared display-controller contract for Tegra DRM. It defines the CRTC state, display-controller instance state, SoC capability descriptions, window programming data, public DC helper prototypes, RGB helper prototypes, and the display-controller register/bitfield map used by `dc.c` and output drivers.

## Important APIs, Types, and Definitions
`struct tegra_dc_state` extends `drm_crtc_state` with the selected parent clock, pixel clock, shift-clock divider, and a bitmask of planes that need update/activate requests. `struct tegra_dc_stats` stores frame, vblank, underflow, and overflow counters for the current active interval and total device lifetime. `struct tegra_dc_soc_info` describes per-generation feature support such as cursor, block-linear layout, sector layout, legacy blending, powergate, coupled PM, NVdisplay, pitch alignment, window groups, supported formats/modifiers, filter limitations, and PLL availability.

`struct tegra_dc` is the device object embedded around a host1x client and DRM CRTC. It stores syncpoint, device, pipe, clock/reset/register/IRQ handles, RGB output, stats, debugfs files, SoC info, and OPP availability. `struct tegra_dc_window` is the transient plane programming payload consumed by `dc.c`; it carries source/destination rectangles, bpp, strides, base addresses, zpos, reflection flags, tiling, hardware color format, and byte swap.

The header provides inline register accessors `tegra_dc_writel()` and `tegra_dc_readl()` with trace hooks, and conversion helpers from DRM/host1x objects to Tegra objects.

## Control Flow Role
The header itself has no runtime control flow, but it encodes the register protocol that the implementation follows. Important groups include command/syncpoint/state-control registers, interrupt status/mask/type/polarity bits, display timing registers, output enable bits for HDMI/DSI/SOR/cursor, cursor address/blending registers, window option/color/stride/address registers, legacy blend registers, CSC/filter registers, and Tegra186+ window-group/NVdisplay register aliases.

## State and Persistence
The persistent state described here is split between DRM atomic state (`tegra_dc_state`), device lifetime state (`tegra_dc`), and hardware state represented by register offsets and bit definitions. The register map documents double/triple-buffered programming via `DC_CMD_STATE_CONTROL` update and activate bits, and it exposes both legacy DC window registers and later NVdisplay window-group registers.

## Dependencies and Integration Points
`dc.h` includes Linux host1x and DRM CRTC headers and includes local `drm.h`. It is consumed by display controller implementation, RGB, DSI, SOR/HDMI paths, and code that needs to call `tegra_dc_state_setup_clock()` or `tegra_dc_commit()`. Register definitions integrate with tracepoints through the inline accessors.

## Risks
The header contains many raw register constants with overlapping aliases between legacy and Tegra186+ programming models. Incorrect use of a legacy offset against an NVdisplay window group, or vice versa, can silently program the wrong register. Some bitfield masks include comments noting wider fields on Tegra186, so callers must account for `tegra->hmask`/`vmask` and SoC limits. Because this file is the canonical register vocabulary, stale or incorrect constants have broad blast radius across modesetting, plane updates, interrupts, and output enable paths.

## Test Signals
Build coverage should catch missing prototypes and type drift. Runtime validation comes from successful modesets on each supported SoC generation, trace logs showing expected register offsets, debugfs register dumps matching hardware documentation, correct interrupt status handling, and format/modifier tests that exercise the window color-depth and tiling constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.c

## Purpose
`dp.c` provides reusable DisplayPort/eDP link-management logic for the Tegra DRM driver. It probes sink capabilities over AUX, stores link capability/configuration state, chooses a lane/rate combination for a mode, configures DPCD link registers, and performs fast or full link training with voltage swing, pre-emphasis, post-cursor, channel equalization, and fallback rate downgrade.

## Important APIs, Types, and Functions
The public API includes `drm_dp_link_caps_copy()`, `drm_dp_link_add_rate()`, `drm_dp_link_remove_rate()`, `drm_dp_link_update_rates()`, `drm_dp_link_probe()`, `drm_dp_link_configure()`, `drm_dp_link_choose()`, `drm_dp_link_train_init()`, and `drm_dp_link_train()`. These operate on the `struct drm_dp_link`, `struct drm_dp_link_caps`, and `struct drm_dp_link_train` types declared in `dp.h`.

Training is split into helpers: `drm_dp_link_apply_training()` calls the hardware-specific `link->ops->apply_training()` hook, writes DPCD training lane settings, optional post-cursor settings, and the training pattern. `drm_dp_link_clock_recovery()` loops pattern 1 recovery. `drm_dp_link_channel_equalization()` loops pattern 2 or 3 equalization. `drm_dp_link_train_full()` configures and retries with downgraded rates. `drm_dp_link_train_fast()` uses fixed pattern delays before checking final link status.

## Control Flow
`drm_dp_link_probe()` resets the link object, reads receiver capability DPCD bytes, fills revision/max rate/max lanes/capability flags, handles alternate scrambler reset and eDP revision lookup, computes clock-recovery and channel-equalization AUX read intervals, initializes current rate/lanes to max, and parses eDP 1.4 supported link rates if available.

`drm_dp_link_choose()` computes mode bandwidth from pixel clock and bits per color, then searches lanes `{1,2,4}` and link rates `{162000,270000,540000}` for the lowest combination with enough 8b/10b-adjusted capacity within sink limits. `drm_dp_link_configure()` optionally calls the driver-specific configure hook, writes link bandwidth/lane count/enhanced framing, writes channel coding, and enables alternate scrambler reset when supported.

`drm_dp_link_train()` reinitializes training state, attempts fast training only if the sink supports it and valid previous settings are already available, then falls back to full training. In this implementation fast training is effectively unreachable after reinitialization because `drm_dp_link_train_valid()` sees the freshly reset state as not recovered/equalized. Full training configures the link, runs clock recovery up to four iterations, downgrades from HBR2 to HBR to RBR on failure, runs channel equalization similarly, and always disables training before returning.

## State and Persistence
`struct drm_dp_link` persists sink capabilities, current selected rate and lanes, parsed additional eDP rates, read intervals, DPCD/eDP revision, driver hooks, AUX pointer, and training state. Training request and adjustment arrays persist per train invocation. No state is written to disk; hardware/sink state is persisted by DPCD writes and source-specific hooks.

## Dependencies and Integration Points
The file depends on DRM DP helper DPCD accessors, DRM display modes, and `link->ops` supplied by the hardware-specific output driver. It does not touch Tegra registers directly. It expects a working `struct drm_dp_aux`, usually backed by `dpaux.c`, and is typically used by SOR/eDP output code that supplies source-side training register programming.

## Risks
Training retry behavior only downgrades the rate, not the lane count, so some marginal sinks may fail even if fewer lanes at a lower rate would work. `drm_dp_link_choose()` ignores eDP 1.4 custom supported-rate arrays when choosing from the fixed three-rate table. The fast-training path resets state before validity testing, so it will not use previously learned settings as written. AUX errors propagate directly and can abort modeset. DPCD parsing and interval defaults are sensitive to DP revision rules.

## Test Signals
Signals include successful DPCD capability reads, correct lane/rate selection for representative modes and bpc values, DPCD writes to `DP_LINK_BW_SET`, lane count, channel coding, and eDP configuration, training success across RBR/HBR/HBR2 sinks, downgrade logs when high rates fail, no lingering training pattern after failure, and hotplug/modeset tests on panels requiring TPS2/TPS3 and alternate scrambler reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.h

## Purpose
`dp.h` declares the Tegra-local DisplayPort link abstraction used by `dp.c` and hardware-specific DP/SOR code. It stores sink capabilities, selected link configuration, eDP supported rates, training state, and source-side operation callbacks.

## Important APIs, Types, and Definitions
`struct drm_dp_link_caps` records enhanced framing, TPS3, fast training, ANSI 8b/10b channel coding, and eDP alternate scrambler reset support. `struct drm_dp_link_ops` provides source-specific hooks for applying training parameters and configuring source hardware. `struct drm_dp_link_train_set` carries per-lane voltage swing, pre-emphasis, and post-cursor levels. `struct drm_dp_link_train` carries requested and sink-adjusted settings plus current pattern and success flags. `struct drm_dp_link` ties all of that to DPCD/eDP revisions, max/current rate and lanes, AUX read intervals, optional eDP rates, operation hooks, AUX channel, and training state.

Macros such as `DP_TRAIN_VOLTAGE_SWING_LEVEL()`, `DP_TRAIN_PRE_EMPHASIS_LEVEL()`, and `DP_LANE_POST_CURSOR()` encode DPCD training fields.

## Control Flow Role
The header is passive but defines how DP code is sequenced: callers probe into `drm_dp_link`, optionally choose a mode-specific configuration, configure DPCD/source hardware, and train through `drm_dp_link_train()`. Source drivers must fill `ops` and `aux` before training if hardware register programming is required.

## State and Persistence
The key persistent runtime state is the `struct drm_dp_link` instance owned by an output driver. It tracks probed capabilities and currently selected rate/lane count across link setup. Training state is embedded and updated during link training only.

## Dependencies and Integration Points
The header includes Linux types and forward-declares DRM display/AUX types. It depends on DP helper constants such as `DP_MAX_SUPPORTED_RATES` being visible to consumers through included DRM DP helper headers in implementation files. It integrates with `dpaux.c` through `struct drm_dp_aux` and with source drivers through `drm_dp_link_ops`.

## Risks
Because this is a local helper abstraction named with `drm_dp_*`, it can be confused with upstream DRM core helpers. Consumers must initialize `aux` and `ops` correctly or `drm_dp_link_apply_training()` can dereference missing hooks. The fixed array sizes assume DP helper constants and four-lane DP semantics.

## Test Signals
Build tests should verify all consumers see the same struct layout and prototypes. Runtime tests should verify that a link object survives probe, configure, choose, and train sequences, and that source-specific hooks receive the requested per-lane training values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.c

## Purpose
`dpaux.c` implements the Tegra DisplayPort AUX controller platform driver and exposes it as a DRM `struct drm_dp_aux`. It handles AUX and I2C-over-AUX transactions, HPD plug/unplug IRQs, AUX bus population, optional panel power polling, pad muxing between AUX/I2C/off modes, runtime PM, clock/reset/regulator sequencing, and global lookup by device tree node.

## Important APIs, Types, and Functions
`struct tegra_dpaux` embeds `struct drm_dp_aux`, the device/register/IRQ handles, output attachment, reset and clock handles, optional regulator, transaction completion, hotplug work item, global list entry, and optional pinctrl state. `struct tegra_dpaux_soc` stores pad drive calibration constants.

The public helpers declared in `drm.h` are `drm_dp_aux_find_by_of_node()`, `drm_dp_aux_attach()`, `drm_dp_aux_detach()`, `drm_dp_aux_detect()`, `drm_dp_aux_enable()`, and `drm_dp_aux_disable()`. Core transport is `tegra_dpaux_transfer()`, installed as `aux.transfer`. IRQ and hotplug handling are in `tegra_dpaux_irq()` and `tegra_dpaux_hotplug()`.

## Control Flow
Probe allocates the controller, stores SoC data, initializes work/completion/list state, maps registers, gets IRQ/reset/clocks/regulator, sets the parent clock rate to 270 MHz, enables runtime PM and takes an initial PM reference, requests and disables the IRQ, initializes the DRM AUX object, configures pads to I2C mode for HDMI by default, optionally registers pinctrl, enables/clears AUX interrupts, adds the object to a global mutex-protected list, and populates DP AUX bus endpoint devices.

Each AUX transfer validates the 16-byte FIFO limit, encodes zero-length I2C address-only transactions when allowed, maps DRM AUX requests to Tegra command bits, writes address/control and optional write FIFO data, sets `TRANSACTREQ`, waits for completion signaled by IRQ, reads and clears status, maps hardware timeout/RX/sink/no-stop errors to Linux errors, translates hardware reply type to DRM AUX reply codes, and reads back FIFO data for successful reads with exact-length validation.

Attach registers the AUX channel with DRM, stores the output, enables HPD polling, optionally enables panel VDD, polls HPD connected for up to 250 ms, then enables IRQ. Detach unregisters AUX, disables IRQ, optionally disables panel VDD and polls for disconnect, then clears output for panel-backed paths. Runtime suspend asserts reset and disables clocks; resume enables clocks and deasserts reset.

## State and Persistence
Persistent in-memory state includes the global `dpaux_list`, each `tegra_dpaux` object, its output pointer, completion object, work item, pinctrl device, and regulator/clock/reset handles. Hardware state includes pad mode/power, interrupt enable/status, AUX transaction registers, and HPD status. There is no disk persistence.

## Dependencies and Integration Points
The file integrates with DRM DP helper APIs, DRM AUX bus population, DRM panel and HPD helpers, Tegra tracepoints, Linux platform/PM/clock/reset/regulator subsystems, pinctrl/pinmux when enabled, and output drivers that find a DPAUX node and attach a `tegra_output`.

## Risks
The transfer path depends on IRQ completion and can timeout if IRQs are disabled or status bits are missed. Read response length mismatch is converted to `-EBUSY` to trigger helper retries, which is intentional but can hide hardware quirks. `drm_dp_aux_attach()` returns early on regulator/panel polling failures after AUX registration or regulator enable without fully unwinding all intermediate state. `drm_dp_aux_detach()` clears `output` only in the panel path, so non-panel detach keeps a stale pointer until reattach/remove. Pad mux defaults to I2C for HDMI, so DP paths must call enable/disable at the right time.

## Test Signals
Useful validation includes AUX native reads of DPCD, I2C-over-AUX EDID reads, retry behavior under short replies, HPD plug/unplug IRQ work firing `drm_helper_hpd_irq_event()`, panel-backed attach/disconnect polling, runtime suspend/resume preserving transaction ability, pinctrl mode changes for `aux`, `i2c`, and `off`, and trace logs showing expected AUX register writes/status clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.h

## Purpose
`dpaux.h` defines the Tegra DPAUX hardware register offsets and bitfields used by `dpaux.c`. It is a compact register map for AUX transactions, HPD interrupts, pad control, scratch registers, and hybrid AUX/I2C pad modes.

## Important APIs, Types, and Definitions
The header contains no structs or functions. Key definitions include interrupt registers and bits (`DPAUX_INTR_EN_AUX`, `DPAUX_INTR_AUX_DONE`, plug/unplug/IRQ events), data FIFO windows (`DPAUX_DP_AUXDATA_WRITE()` and `DPAUX_DP_AUXDATA_READ()`), address/control/status registers, AUX command encodings for native and I2C requests, address-only and command-length fields, status error and reply masks, HPD timing registers, AUX configuration, hybrid pad control drive/input/mode fields, pad power-down bit, and scratch registers.

## Control Flow Role
`dpaux.c` uses these constants to encode each transaction: write FIFO data, set address and command, trigger the transaction, decode completion status, map reply types, and switch pads between AUX, I2C, and powered-down states. The IRQ handler uses the interrupt bits to distinguish transaction completion from HPD events.

## State and Persistence
The header describes volatile hardware state only. Transaction status, reply type, HPD status, and pad power/mode persist in registers until changed or cleared by the driver.

## Dependencies and Integration Points
It is consumed by the DPAUX platform driver. The command definitions map DRM AUX request types to Tegra-specific control bits, while HPD and pad definitions integrate with DRM connector detection and Linux pinctrl.

## Risks
Incorrect command encoding can turn native AUX reads into I2C operations or mis-handle MOT/address-only transactions. Error mask definitions directly affect whether transactions retry, timeout, or fail with I/O errors. Pad control bit mistakes can break both DP AUX and HDMI DDC because the same hybrid pads are shared.

## Test Signals
Register-level validation comes from successful DPCD reads, EDID I2C-over-AUX reads, HPD status changes, and pad mux transitions. Trace output from `tegra_dpaux_readl/writel` should show status bits being cleared after each transaction and expected hybrid pad mode values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dpaux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.c

## Purpose
`drm.c` is the top-level Tegra DRM/host1x driver. It registers the host1x DRM driver and all Tegra display/engine platform drivers, allocates and registers the DRM device, wires atomic modesetting, manages per-file contexts, provides legacy/staging render ioctls, submits host1x jobs, manages shared IOMMU/GEM carveout allocation, initializes debugfs, and handles system suspend/resume/shutdown.

## Important APIs, Types, and Functions
The DRM driver object is `tegra_drm_driver`; host1x integration is `host1x_drm_driver`; platform subdrivers are listed in `drivers[]`. Mode configuration uses `tegra_atomic_check()` and `tegra_atomic_commit_tail()`. Client registration exports `tegra_drm_register_client()` and `tegra_drm_unregister_client()`. IOMMU helpers are `host1x_client_iommu_attach()` and `host1x_client_iommu_detach()`. Shared allocation helpers are `tegra_drm_alloc()` and `tegra_drm_free()`.

The main UAPI submit path is `tegra_drm_submit()`, which validates command buffers, relocations, syncpoints, pins host1x jobs, submits them, and returns a fence value. Per-file setup/cleanup is in `tegra_drm_open()` and `tegra_drm_postclose()`.

## Control Flow
Module init first refuses to load when firmware-only DRM drivers are requested, then registers the host1x DRM driver and the Tegra platform drivers. `host1x_drm_probe()` allocates `drm_device` and `tegra_drm`, optionally creates an IOMMU paging domain, initializes mode config and polling, initializes all host1x subdevices, computes display masks and IOMMU carveout/GEM apertures if explicit IOMMU attachment was used, prepares the display hub, initializes VBLANK, resets mode config, removes conflicting firmware framebuffers if CRTCs exist, disables modeset/atomic features if no CRTC exists, registers the DRM device, and starts DRM clients.

Atomic commit uses the display-hub-specific sequence when `tegra->hub` exists: disables, hub commit, plane commit, enables, hardware done, wait for vblanks, cleanup, and post-commit bandwidth handling. Without hub it delegates to `drm_atomic_helper_commit_tail_rpm()`.

`tegra_drm_submit()` copies user command buffer, relocation, and syncpoint arrays; rejects unsupported wait checks and multiple syncpoint increments; allocates a host1x job; validates gather word count, object existence, offset alignment, and object bounds; resolves relocation BO references; obtains the syncpoint; assigns class/register validators; pins and submits the job; stores the resulting fence threshold; drops all GEM references and job references on exit.

## State and Persistence
`struct tegra_drm` persists the DRM pointer, optional IOMMU domain, explicit-IOMMU flag, DRM MM allocator, carveout IOVA domain parameters, client list, pitch alignment, display masks, CRTC count, and display hub pointer. Each open file receives `struct tegra_drm_file` with legacy IDR contexts, xarray contexts, syncpoints, and a mutex. Each render context stores the client, host1x channel, legacy id, new-UAPI mappings, and optional memory context. State is process/device lifetime only.

## Dependencies and Integration Points
The file integrates with DRM core, DRM atomic helpers, fbdev/client setup, PRIME/GEM helpers, host1x bus, Tegra GEM/UAPI code, display hub/DC/output drivers, Linux IOMMU/IOVA/drm_mm, runtime PM on clients, firmware framebuffer aperture removal, debugfs, and all listed Tegra platform subdrivers.

## Risks
The submit path is security-sensitive because it copies user pointers and patches command streams; alignment, bounds, syncpoint, and relocation checks are critical. IOMMU policy is subtle: the driver avoids GART, requires host1x consistency, and may tear down an allocated domain if no client attaches explicitly. Error paths in probe must unwind mode config, hub, IOMMU, iova cache, host1x subdevices, and DRM refs in the right order. The no-CRTC case intentionally clears modeset features, so render-only SoCs depend on that path. Legacy staging ioctls and new UAPI coexist in per-file cleanup.

## Test Signals
Signals include successful module init/unload, DRM registration with and without display CRTCs, correct platform subdriver binding, IOMMU aperture debug logs and debugfs `iova` output, host1x client register/unregister, render job submission with valid and invalid gathers/relocs, GEM tiling/flag ioctls under staging, clean per-file close cleanup, suspend/resume through DRM helpers, and no leaked IOVA/DRM MM ranges after buffer allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.h

## Purpose
`drm.h` is the central internal Tegra DRM header. It defines the top-level `struct tegra_drm`, per-client and per-context render abstractions, the generic output wrapper, framebuffer/helper prototypes, DPAUX helper prototypes, memory allocation helpers, and external platform driver declarations used by module registration.

## Important APIs, Types, and Definitions
`struct tegra_drm` stores global device state: DRM device, optional IOMMU domain, DRM MM and carveout IOVA allocators, client list, display masks, pitch alignment, CRTC count, and display hub pointer. `struct tegra_drm_client` wraps `host1x_client` with list membership, backpointer, shared channel, version, and operation table. `struct tegra_drm_context` stores a client/channel pair plus legacy and new-UAPI context state. `struct tegra_drm_client_ops` defines client-specific channel open/close, class/register validation, submit, stream ID, and memory-context support callbacks.

`struct tegra_output` wraps common output resources: OF node, device, bridge/panel/DDC/EDID/CEC/HPD resources, encoder, and connector. Inline helpers convert DRM encoder/connector and host1x client pointers back to Tegra wrappers.

## Control Flow Role
The header defines cross-file contracts rather than runtime behavior. Render clients register with `tegra_drm_register_client()`, contexts submit through `tegra_drm_submit()` or client-specific no-op fallback, outputs probe/init/exit through `output.c`, DPAUX-backed outputs find/attach/enable AUX, and framebuffer code exposes Tegra BO planes, tiling, allocation, and creation.

## State and Persistence
All types are in-memory lifetime state. `tegra_drm` is DRM-device lifetime. `tegra_drm_client` is platform/host1x-client lifetime. `tegra_drm_context` is file/context lifetime. `tegra_output` is output-device lifetime and stores connector/encoder objects embedded by value.

## Dependencies and Integration Points
The header includes host1x, IOVA, GPIO, DRM atomic/bridge/encoder/fixed/probe helper headers, Tegra UAPI, and local GEM/hub/trace headers. It connects `drm.c`, `dc.c`, `dsi.c`, `dpaux.c`, framebuffer/GEM/output code, and all declared Tegra platform drivers.

## Risks
Because this is the central internal ABI, struct layout or ownership changes can ripple through many drivers. Embedded DRM connector/encoder objects require strict cleanup ordering. `tegra_drm_client_ops` callbacks are optional in some paths but mandatory in others, so missing hooks can lead to `-ENOSYS` or crashes depending on caller assumptions. The local `DRM_FORMAT_MOD_NVIDIA_SECTOR_LAYOUT` definition is marked as a candidate for UAPI relocation, so modifier compatibility must be watched.

## Test Signals
Build coverage across all Tegra DRM objects is the main static signal. Runtime signals include correct output connector/encoder creation, client registration lists, successful context open/close/submit for engines, DPAUX helper linkage, framebuffer creation with expected tiling/modifiers, and module registration resolving all external platform-driver symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.c

## Purpose
`dsi.c` implements the Tegra MIPI DSI host and DRM encoder/connector output. It handles DSI register programming, packet sequence selection for video and command mode, D-PHY timing, MIPI calibration, panel prepare/enable sequencing, host FIFO transfers, runtime PM, regulator/clock/reset control, debugfs register dumps, and optional dual-channel ganged-mode operation.

## Important APIs, Types, and Functions
`struct tegra_dsi_state` extends connector state with D-PHY timing, bit period, refresh rate, lane count, pixel and byte clocks, hardware format, and pixel-format multiplier/divider. `struct tegra_dsi` embeds a host1x client, `tegra_output`, MIPI DSI host, register/clock/reset/regulator handles, MIPI calibration handle, FIFO depths, mode flags, format/lanes, debugfs files, and master/slave pointers for ganged mode.

Important flows include `tegra_dsi_encoder_atomic_check()` for clock/timing state calculation, `tegra_dsi_encoder_enable()` and `tegra_dsi_encoder_disable()` for modeset sequencing, `tegra_dsi_configure()` for packet/timing register programming, `tegra_dsi_host_transfer()` for MIPI DSI command transport, `tegra_dsi_host_attach()` and detach for peripheral/panel binding, and host1x/runtime PM callbacks.

## Control Flow
Probe allocates `struct tegra_dsi`, resolves ganged slave if referenced, probes generic output resources, sets default video/RGB888/4-lane mode, gets reset if needed, gets module/LP/parent clocks and regulator, sets clock parent routing, maps registers, requests the MIPI calibration device, registers the MIPI DSI host, enables runtime PM, and registers as a host1x client.

When a DSI peripheral attaches, the host stores mode flags, pixel format, and lane count; if a slave exists it sets up shared PLL parentage. Non-slave instances look up the panel and trigger HPD if a DRM connector already exists. Host1x init creates the DRM DSI connector and simple encoder for non-slave instances, attaches helpers, registers the connector, initializes generic output resources, and sets possible CRTCs.

Atomic check computes pixel clock, format multiplier/divider, aggregate lane count, hardware DSI format, vrefresh, byte clock, bit clock rounded to MHz, D-PHY timing defaults/validation, halves PLLD for hardware constraints, calculates shift-clock divider, and stores the selected DSI parent clock into the DC CRTC state. Encoder enable resumes host1x/runtime resources, enables MIPI calibration, calibrates pads, sets timeouts and PHY timing, prepares the panel, configures packet sequencing and horizontal packet lengths, enables the DC DSI output bit, commits DC state, powers DSI, and enables the panel. Disable reverses panel/video/DC state, waits idle, soft-resets, unprepares panel, powers DSI down, disables MIPI calibration, and suspends host1x resources.

Host transfer creates a MIPI packet, validates FIFO capacity, clears FIFO error flags, powers the controller, configures host control for HS/LP, host/video FIFO selection, CRC/ECC, optional BTA, writes header/payload to `DSI_WR_DATA`, triggers host transmission, optionally waits for and parses read/ACK response, and returns either received byte count or transmitted header+payload count.

## State and Persistence
Persistent runtime state includes panel/output binding, DSI host parameters from the attached peripheral, clock/regulator/reset/MIPI handles, FIFO depth constants, master/slave topology, and connector atomic state. Hardware state includes DSI power, control, packet sequence, packet length, timeout, PHY timing, pad, ganged-mode, FIFO, and trigger registers. There is no disk persistence.

## Dependencies and Integration Points
The file integrates with DRM connector/encoder helpers, generic Tegra output handling, Tegra DC clock setup and output-enable registers, MIPI DSI host APIs, DRM panel APIs, MIPI D-PHY timing helpers, Tegra MIPI calibration, host1x client lifecycle, runtime PM, clocks, reset, regulator, OF platform lookup, and local `dsi.h` register definitions.

## Risks
The DSI enable/disable order is panel- and hardware-sensitive; changing panel prepare/enable, DC DSI bit, DSI power, soft reset, or MIPI calibration order can break panels. `tegra_dsi_read_response()` appears to index `rx[j + k]` after already offsetting `rx = msg->rx_buf + j`, which is suspicious for long responses and deserves targeted review. Ganged mode assumes symmetric left/right split and shared PLL setup. `tegra_dsi_prepare()` logs MIPI enable/calibration failures but still returns 0 after those failures, so later register programming may proceed on a bad PHY. Packet length arithmetic subtracts fixed overhead and could underflow for invalid tiny modes if not filtered elsewhere.

## Test Signals
Signals include panel attach/detach HPD events, successful video-mode and command-mode panel enable, D-PHY timing validation, stable byte/bit clock and DC shift divider values, MIPI DCS reads/writes through host transfer, FIFO overflow/underflow recovery, idle wait success on disable, runtime PM cycles, debugfs `regs` while active, ganged dual-channel panels with correct left/right split, and no panel artifacts across suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.h

## Purpose
`dsi.h` defines the Tegra DSI controller register offsets, bitfields, timeout/tally helpers, pad/ganged-mode fields, and hardware pixel-format enum used by `dsi.c`.

## Important APIs, Types, and Definitions
The header has no functions. It defines DSI syncpoint/context/FIFO/power/interrupt/control/status registers; host control bits for FIFO/CRC resets, transmit trigger source, raw/HS/FIFO/BTA/CRC/ECC behavior; DSI control fields for HS clock, virtual channel, format, lanes, source, video, host, and DCS mode; packet sequence and packet length registers; PHY timing and BTA timing fields through `DSI_TIMING_FIELD()`; timeout/tally fields; pad pull-down/slew/pre-emphasis fields; ganged mode start/size/control registers; raw byte-count and ultra-low-power registers; and `enum tegra_dsi_format` values used in `DSI_CONTROL_FORMAT`.

## Control Flow Role
`dsi.c` uses these definitions to configure video or command packet sequencing, host-mode DSI writes/reads, D-PHY timing, timeout handling, pad calibration, power enable/disable, ganged dual-channel windows, and status polling. The `DSI_TIMING_FIELD()` macro converts timing values and byte-clock period into packed hardware fields.

## State and Persistence
The header describes volatile DSI hardware state. Power, trigger, FIFO, packet sequence, timing, pad, timeout, and ganged-mode settings persist in controller registers until reset or reprogrammed.

## Dependencies and Integration Points
It is consumed by the Tegra DSI host/encoder implementation and indirectly connects MIPI DSI protocol concepts to Tegra-specific registers. It also relies on kernel math macros such as `DIV_ROUND_CLOSEST()` being available in the including C file.

## Risks
Most definitions are low-level bit encodings; mistakes can corrupt packet sequencing, D-PHY timing, or pad drive behavior. `DSI_TIMING_FIELD()` subtracts a hardware increment and masks to 8 bits, so invalid periods or undersized timings can wrap if not validated first. Host and video enable bits share `DSI_CONTROL`, so callers must avoid leaving conflicting modes enabled.

## Test Signals
Runtime validation comes from successful DSI panel modesets, DCS command transfers, stable PHY timing on a scope or through panel behavior, no FIFO underflow/overflow status after transfers, correct ganged-mode register values for dual-channel panels, and trace/debugfs register dumps matching the intended packet sequence and timing configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.h -->
