# subset-b-003693 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c

## Purpose
`dsi.c` is the OMAP DRM Display Subsystem MIPI DSI host and bridge implementation. It owns the DSI protocol engine, PHY, DSI PLL, virtual channels, command/video mode setup, external TE handling, MIPI DSI host callbacks, DRM bridge callbacks, component binding, and runtime PM integration for OMAP3, OMAP4, and OMAP5 DSI blocks.

## Important APIs, types, and functions
The file centers on `struct dsi_data` from `dsi.h`, with register access helpers `dsi_read_reg()` and `dsi_write_reg()`. The MIPI host entry points are `omap_dsi_host_attach()`, `omap_dsi_host_detach()`, and `omap_dsi_host_transfer()`. DRM bridge operations are `dsi_bridge_mode_valid()`, `dsi_bridge_mode_set()`, `dsi_bridge_enable()`, and `dsi_bridge_disable()`. Component and platform lifecycle code is handled by `dsi_bind()`, `dsi_unbind()`, `dsi_probe()`, and `dsi_remove()`.

Important internal subsystems include IRQ registration through `dsi_register_isr()` and `dsi_register_isr_vc()`, PLL and clock setup through `dsi_pll_enable()`, `dsi_configure_dsi_clocks()`, `dsi_cm_calc()`, and `dsi_vm_calc()`, PHY/CIO setup through `dsi_cio_init()`, lane setup through `dsi_configure_pins()` and `dsi_set_lane_config()`, packet IO through `dsi_vc_send_short()`, `dsi_vc_send_long()`, `dsi_vc_read_rx_fifo()`, and update handling through `dsi_update_channel()`.

## Control flow
Probe maps the `proto`, `phy`, and `pll` register windows, requests the shared IRQ, gets the DSI regulator and clock, resolves SoC-specific quirks and module ID, parses endpoint lane data, registers the MIPI DSI host, initializes an OMAP DSS output, and joins the DSS component graph. Bind registers the DSI PLL with the DSS PLL framework and installs debugfs views.

On panel attach, the host records command or video mode, pixel format, high-speed and low-power clock limits, transfer mode, and optional TE GPIO state. Mode validation and mode set run `__dsi_calc_config()`, which selects DSI PLL, DISPC divider, LP clock, DISPC videomode, and DSI video timing values. Bridge enable cancels delayed disable work, locks the DSI bus, powers and configures the interface if needed, initializes DISPC output, and enables video output. Bridge disable reverses the output, DISPC, DSI interface, CIO, PLL, and runtime PM state.

Command transfers use virtual channel `VC_CMD`, opportunistically enable the DSI block when it is idle, send packets in LP or HS mode based on `MIPI_DSI_MSG_USE_LPM`, and use BTA synchronization for writes and reads. Video output uses `VC_VIDEO`, configures the video port path, and in command mode performs explicit DISPC updates with framedone and TE timeout handling.

## State and persistence
Persistent in-memory state includes calculated PLL clocks, LP clocks, DISPC dividers, videomode timings, selected MIPI mode and pixel format, lane mapping, virtual channel source and FIFO allocations, TE GPIO and IRQ state, delayed works, error bits, IRQ tables, and debugfs entries. Hardware state persists in DSI protocol, PHY, PLL, and DSS clock mux registers until disabled, reset, or runtime suspended. Runtime suspend gates IRQ handling with `is_enabled` and synchronizes the IRQ before power down; it does not perform a full register context save in this file.

## Dependencies and integration points
The file integrates with the DRM bridge chain, DRM panel/MIPI DSI core, OMAP DSS output helpers, DISPC manager programming, DSS clock-source selection, the common DSS PLL framework, runtime PM, regulators, GPIO descriptors, IRQs, syscon pad muxing on OMAP4/5, device tree graph endpoints, and optional debugfs/IRQ statistics.

## Risks
The highest risks are timing and state ordering bugs. DSI clock calculation is tightly coupled to lane count, pixel format, line buffer size, transfer mode, and panel clock tolerances. Incorrect lane mappings or SoC quirk selection can leave PHY lanes disabled or inverted. Packet paths assume the DSI bus semaphore is held and use short timeouts around hardware FIFO and BTA state; races can deadlock updates or lose errors. Command-mode update completion is fragile: missing TE or framedone events rely on timeout work, and the comments note that canceling hardware transfers is buggy. Runtime PM must preserve IRQ ordering through `is_enabled` and `synchronize_irq()`.

## Test signals
Useful signals include successful probe and component bind on OMAP3/4/5 device trees, MIPI DSI host attach/detach, mode validation for expected panel modes, LP and HS command transfers, DCS reads and writes with BTA completion, TE-on and TE-off command behavior, command-mode full-screen updates with framedone, video-mode continuous output, suspend/resume cycles, debugfs register/clock dumps, absence of DSI IRQ error bits, and panel conformance tests across RGB565, RGB666, and RGB888.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h

## Purpose
`dsi.h` is the private DSI register, interrupt, timing, clock, and state definition header for the OMAP DSI implementation. It names the protocol, PHY, and PLL register windows, exposes hardware bit masks used by `dsi.c`, and defines the core data structures that carry DSI configuration and runtime state.

## Important APIs, types, and functions
`struct dsi_reg` and `DSI_REG()` encode a register as module plus offset, allowing `dsi.c` to dispatch accesses to protocol, PHY, or PLL bases. Register macros cover global DSI control and IRQ registers, per-virtual-channel registers, DSIPHY configuration registers, and DSI PLL registers. Interrupt masks define global, virtual-channel, and ComplexIO error and event bits.

Configuration types include `enum omap_dss_dsi_mode`, `enum omap_dss_dsi_trans_mode`, `struct omap_dss_dsi_videomode_timings`, and `struct omap_dss_dsi_config`. Runtime and hardware description types include `struct dsi_data`, `struct dsi_of_data`, `struct dsi_clk_calc_ctx`, `struct dsi_lane_config`, `struct dsi_isr_tables`, `struct dsi_irq_stats`, and `struct dsi_lp_clock_info`.

## Control flow
The header has no executable control flow, but it establishes the contracts used by `dsi.c`. SoC match data fills `struct dsi_of_data`, probe populates `struct dsi_data`, lane parsing fills the `lanes` array, host attach fills the public DSI config, clock calculation uses `struct dsi_clk_calc_ctx`, bridge enable programs values into hardware, and IRQ handling consults the ISR table arrays and masks declared here.

## State and persistence
The key persistent driver state is stored in `struct dsi_data`: mapped register bases, module ID, IRQ, runtime enabled flags, clocks, syscon, DSS pointer, MIPI host, calculated clock structures, PLL object, regulator state, attached MIPI device, per-VC FIFO/source state, bus and mutex locks, IRQ tables, update state, TE state, delayed work, cached clock values, error bits, debugfs pointers, lane configuration, DSI mode, videomode, DSS output, DRM bridge, and delayed disable work. This state survives across individual transfers and is reset only through detach, bridge disable, remove, or power-management paths.

## Dependencies and integration points
The header depends on DRM MIPI DSI declarations and OMAP DSS types included indirectly through users. Its structures are shared with the OMAP DSS PLL, DISPC clock, DRM bridge, runtime PM, regulator, GPIO, and debugfs paths in `dsi.c`. It also encodes SoC quirks that determine behavior for OMAP3, OMAP4, and OMAP5 hardware.

## Risks
Because this header describes bit positions and packed state, incorrect register offsets or masks can silently program the wrong hardware field. The interrupt masks are safety critical for error reporting and transfer completion. `struct dsi_data` is concurrency-sensitive because several fields are touched under different locks (`lock`, `bus_lock`, `irq_lock`, and `errors_lock`); adding fields without matching lock discipline can introduce races.

## Test signals
Build coverage should compile all DSI-enabled OMAP DRM code paths. Runtime signals are successful register dumps, correct SoC module detection, working PLL and lane setup on supported SoCs, IRQ statistics matching actual traffic, successful MIPI DSI transfers, and command/video mode operation without error IRQ masks being latched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c

## Purpose
`dss.c` is the OMAP Display Subsystem hardware core and component master. It manages DSS register access, SoC feature data, functional clocks, LCD/DISPC/DSI/HDMI/VENC clock source muxing, SDI setup, video PLL discovery, debugfs, runtime PM context handling, child component collection, and creation of the `omapdrm` platform device after all DSS children bind.

## Important APIs, types, and functions
External APIs implemented here include `dss_runtime_get()`, `dss_runtime_put()`, `dss_get_device()`, `dss_get_dispc_clk_rate()`, `dss_get_max_fck_rate()`, `dss_select_dsi_clk_source()`, `dss_select_lcd_clk_source()`, `dss_get_*_clk_source()`, `dss_select_hdmi_venc_clk_source()`, `dss_dpi_select_source()`, `dss_div_calc()`, and SDI helpers. Internal types `struct dss_ops` and `struct dss_features` describe SoC-specific routing, clock limits, supported ports, supported outputs, and register field layouts.

## Control flow
Probe allocates `struct dss_device`, maps DSS registers, selects a feature table from SoC match data or device tree compatible data, obtains clocks, programs a default DSS functional clock, probes video PLLs, initializes DPI/SDI ports from graph ports, enables runtime PM, probes hardware revision and default mux state, initializes debugfs, populates child platform devices, gathers OMAP DSS components, and registers as a component master. Master bind first binds all child components, disables VT switching, and registers the top-level `omapdrm` platform device with a `dss_pdata` pointer.

Clock selection paths program `DSS_CONTROL` fields or syscon PLL control bits depending on SoC. OMAP2/3 share DISPC and LCD clock source behavior, while OMAP4/5/DRA7 have per-LCD mux functions. Runtime suspend saves selected DSS registers, lowers bus throughput, and selects sleep pinctrl; runtime resume restores pinctrl, requests high throughput, and restores saved DSS context.

## State and persistence
`struct dss_device` stores mapped registers, syscon PLL control, child DRM device, clocks and cached rates, clock source selections, saved register context, feature table, debugfs entries, video PLL pointers, DISPC pointer, and manager operation state. Hardware register state includes DSS control muxes, SDI control, PLL control, and VENC/HDMI routing. Saved context persists across runtime suspend in `ctx` when `ctx_valid` is set.

## Dependencies and integration points
The file integrates with platform devices, OF graph parsing, component framework, DISPC, DSI, VENC, HDMI4/5, DPI, SDI, OMAP DSS helper APIs, DSS PLL code, regulators, syscon regmap, clocks, pinctrl, runtime PM, debugfs, and system sleep PM. It is the registration point for the DSS driver set through `omap_dss_init()` and `omap_dss_exit()`.

## Risks
SoC feature-table mistakes can route clocks to unsupported outputs or use invalid bit fields. Clock mux functions sometimes return after warnings rather than hard failures, so callers must verify effective state when debugging. Runtime context save only covers core DSS registers, not child components. Component matching recursively walks target modules and skips RFBI by name; device-tree topology changes can alter bind ordering. SDI and clock setup use hardware timeouts and can fail if clocks, pinctrl, or PLL regulators are not ready.

## Test signals
Validation signals include successful platform driver registration, DSS revision logging, child component bind, `omapdrm` platform device creation, debugfs `clk` and `dss` dumps, correct clock-source reports for DPI/DSI/HDMI modes, SDI enable timeout-free operation where supported, suspend/resume without lost DSS mux state, and display smoke tests across each supported SoC feature table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h

## Purpose
`dss.h` is the private OMAP DSS subsystem header. It defines logging and bitfield helpers, DSS model and clock enums, PLL hardware descriptions, LCD manager configuration, the shared `struct dss_device`, and the internal function prototypes used across DSS, DISPC, DSI, DPI, SDI, VENC, HDMI, and PLL implementation files.

## Important APIs, types, and functions
Core definitions include `enum dss_model`, `enum dss_clk_source`, `enum dss_pll_id`, `struct dss_pll_clock_info`, `struct dss_pll_hw`, `struct dss_pll`, `struct dispc_clock_info`, `struct dss_lcd_mgr_config`, and `struct dss_device`. The header declares runtime PM helpers, DSS clock-source selectors, DPI/SDI/DISPC interfaces, debugfs helpers, PLL registration and calculation functions, and external platform driver objects for the DSS hardware modules.

## Control flow
The header does not execute directly. It defines the shared call graph used by `dss.c` to initialize and orchestrate components, by DSI and HDMI code to select clocks and register PLLs, by DISPC to expose manager and overlay functions, and by module init code to register the platform driver set.

## State and persistence
The persistent state model is primarily `struct dss_device`, which holds the DSS register base, syscon PLL control regmap, clock handles and cached rates, selected clock sources, saved context array, feature table, debugfs pointers, PLL objects, DISPC pointer, and manager operations private data. PLL state persists in `struct dss_pll::cinfo`, and LCD manager state is passed through `struct dss_lcd_mgr_config`.

## Dependencies and integration points
The header depends on Linux IRQ declarations and `omapdss.h`, and it ties together the internal DSS display stack. It is the main contract between DSS core, DISPC, DSI, HDMI, DPI, SDI, VENC, and the common PLL helpers. Conditional stubs keep callers buildable when optional subsystems such as debugfs, SDI, DSI, or DPI are disabled.

## Risks
The broad scope makes this a high-coupling header. Changes to PLL structures, clock source enums, or DISPC function prototypes affect many display paths. Bitfield helper macros assume valid bit ranges and 32-bit shifts; misuse can corrupt unrelated register fields. Conditional stubs returning success can hide missing optional functionality during tests unless Kconfig coverage is explicit.

## Test signals
Useful signals include all OMAP DRM Kconfig combinations building, driver registration symbols resolving, PLL calculation tests through DSI/HDMI/video PLL users, DISPC manager and overlay calls still matching prototypes, debugfs enabled and disabled builds, and runtime display tests for each enabled output class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h

## Purpose
`hdmi.h` is the private shared HDMI header for OMAP HDMI implementations. It defines wrapper, PLL, PHY, core audio/video configuration types, register offsets, power-state enums, register access helpers, function prototypes, and the top-level `struct omap_hdmi` state used by HDMI4 code and common HDMI helpers.

## Important APIs, types, and functions
The header names HDMI wrapper registers and IRQ bits, PLL control registers, and PHY registers. It defines enums for PLL and PHY power commands, HDMI versus DVI mode, packing modes, audio format details, audio transfer modes, audio layouts, CTS modes, and MCLK ratios. Major structures include `struct hdmi_config`, `struct hdmi_wp_data`, `struct hdmi_pll_data`, `struct hdmi_phy_data`, `struct hdmi_core_data`, `struct omap_hdmi`, and audio format/DMA/core config types. Inline helpers `hdmi_write_reg()`, `hdmi_read_reg()`, `REG_FLD_MOD()`, `REG_GET()`, and `hdmi_wait_for_bit_change()` provide low-level register access.

## Control flow
The header describes the layered flow used by `hdmi4.c`: wrapper initialization and video programming, PLL initialization and configuration, PHY initialization and lane parsing, core initialization and HDMI4-specific video/audio programming, audio callbacks, CEC integration, DRM bridge operation, and platform lifecycle management. It also exposes common wrapper, PLL, PHY, audio, and lane parsing functions implemented in companion files.

## State and persistence
`struct omap_hdmi` carries mutex-protected display and audio state, platform and DSS pointers, wrapper/PLL/PHY/core blocks, current HDMI config, regulator, core enable state, DSS output and DRM bridge, audio platform device, audio callbacks, idle mode, audio configuration cache, and spinlock-protected audio playback/display booleans. Hardware state persists in wrapper, PLL, PHY, and core registers until bridge disable, core disable, runtime suspend, or remove.

## Dependencies and integration points
The header integrates Linux platform IO, HDMI and CEC framework types, OMAP HDMI audio platform data, DRM bridge, OMAP DSS, and DSS PLL definitions. It is shared by HDMI4 driver code, HDMI core code, CEC code, and common wrapper/PLL/PHY helper implementations.

## Risks
Register offsets and bitfield helpers are a direct hardware ABI. Audio structures combine ALSA, CEA, HDMI wrapper, and core expectations, so changes can break audio silently. `struct omap_hdmi` has mixed mutex and spinlock state; lock ordering must stay consistent between bridge and audio callbacks. Wrapper IRQ masks include hotplug, PLL, video, and audio events, so incorrect masks can produce missed hotplug or audio FIFO faults.

## Test signals
Build coverage should include HDMI4 with and without CEC, HDMI audio, and all common HDMI helpers. Runtime signals include EDID reads, hotplug IRQs, HDMI versus DVI mode selection, AVI infoframe transmission, audio configuration/start/stop, CEC adapter operation, PLL/PHY power transitions, and debugfs register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c

## Purpose
`hdmi4.c` is the OMAP4 HDMI display driver. It binds the HDMI wrapper, PLL, PHY, and HDMI4 core layers into a DRM bridge and OMAP DSS output, handles hotplug/core IRQs, powers the HDMI pipeline, reads EDID, manages CEC physical address updates, registers HDMI audio callbacks, and participates in the DSS component framework.

## Important APIs, types, and functions
Runtime power helpers are `hdmi_runtime_get()` and `hdmi_runtime_put()`. Display power sequencing is split between `hdmi_power_on_core()`, `hdmi_power_off_core()`, `hdmi_power_on_full()`, and `hdmi_power_off_full()`. DRM bridge callbacks are `hdmi4_bridge_attach()`, `hdmi4_bridge_mode_set()`, `hdmi4_bridge_enable()`, `hdmi4_bridge_disable()`, `hdmi4_bridge_hpd_notify()`, and `hdmi4_bridge_edid_read()`. Component lifecycle is `hdmi4_bind()` and `hdmi4_unbind()`, and platform lifecycle is `hdmi4_probe()` and `hdmi4_remove()`. Audio callbacks are exposed through `struct omap_hdmi_audio_ops`.

## Control flow
Probe allocates the bridge-embedded `struct omap_hdmi`, parses lanes, initializes wrapper, PHY, and core blocks, requests the IRQ, gets the `vdda` regulator, enables runtime PM, registers the DSS output, and adds the component. Bind obtains the parent DSS device, initializes the HDMI PLL, initializes optional CEC, registers the HDMI audio platform device, and installs debugfs.

Bridge mode set stores adjusted timings and updates DISPC TV pixel clock. Bridge enable derives HDMI or DVI mode from connector info, builds AVI infoframe data for HDMI sinks, powers the full path, restores cached audio configuration if present, and restarts audio if it was already playing. Full power-on enables the core regulator/runtime PM, selects HDMI clock routing in DSS, computes and programs the HDMI PLL, configures PHY, powers the PHY to LDO, configures wrapper/core video, enables the DSS manager, starts wrapper video, and enables link connect/disconnect IRQs.

IRQ handling acknowledges wrapper IRQs, handles simultaneous connect/disconnect by resetting PHY state, moves PHY to TXON or LDOON for hotplug transitions, and dispatches HDMI core CEC interrupt bit 3 through `hdmi4_cec_irq()`.

## State and persistence
The driver persists current video config in `hdmi->cfg`, core reference count in `core.core_pwr_cnt`, display enable state, cached audio configuration, audio playback state, debugfs handle, audio platform device, and regulator/runtime state. Hardware state spans DSS clock routing, HDMI PLL dividers, PHY power/configuration, wrapper timing and video enable, HDMI core video/audio registers, CEC registers, and IRQ masks.

## Dependencies and integration points
The file depends on DRM atomic bridge state, EDID helpers, OMAP DSS output/manager helpers, DISPC TV clock programming, common HDMI wrapper/PLL/PHY helpers, HDMI4 core helpers, optional CEC helpers, OMAP HDMI audio platform data, regulators, runtime PM, component framework, OF graph lane parsing, and debugfs.

## Risks
Power ordering is sensitive: core power, PLL, PHY, wrapper, DSS manager, video start, and IRQ enables must unwind correctly on errors. EDID reading temporarily enables the core if needed and uses `BUG_ON()` after runtime get, so unexpected PM failure is harsh. Audio callbacks use a spinlock for playback/display flags while configuration uses the mutex; lock use must avoid sleeping under spinlock. Hotplug IRQ handling changes PHY state directly and must keep CEC physical address invalidation in sync with connector state.

## Test signals
Signals include successful probe/bind, debugfs HDMI register dumps, hotplug connect/disconnect IRQs, EDID read and connector update, HDMI and DVI mode display, mode-set PLL/PHY programming, bridge enable/disable without leaks, audio startup/config/start/stop across display on/off transitions, CEC physical address updates, and suspend/resume or repeated hotplug stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c

## Purpose
`hdmi4_cec.c` implements the optional OMAP4 HDMI CEC adapter using the Linux CEC framework. It programs the HDMI core CEC register block, receives and transmits CEC messages, manages logical addresses, enables or disables CEC clocks and IRQs, and maps hardware completion/error events to CEC framework callbacks.

## Important APIs, types, and functions
External functions are `hdmi4_cec_init()`, `hdmi4_cec_uninit()`, `hdmi4_cec_irq()`, and `hdmi4_cec_set_phys_addr()`. Adapter callbacks are `hdmi_cec_adap_enable()`, `hdmi_cec_adap_log_addr()`, and `hdmi_cec_adap_transmit()`. Helper paths include `hdmi_cec_received_msg()`, `hdmi_cec_clear_tx_fifo()`, and `hdmi_cec_clear_rx_fifo()`.

## Control flow
Initialization allocates a CEC adapter with transmit, logical-address, passthrough, and remote-control capabilities, stores the HDMI wrapper pointer in `core->wp`, disables the CEC clock divider initially, and registers the adapter. Enabling CEC powers the HDMI core through `hdmi4_core_enable()`, configures the wrapper CEC clock divider for 2 MHz, clears TX and RX FIFOs, clears pending CEC interrupts, enables wrapper core IRQs, unmasks core CEC IRQ bit 3, enables CEC TX/RX/retry interrupts, and runs CEC calibration. Disable reverses IRQ masks, clears wrapper core IRQ state, disables the CEC clock, and powers down the core reference.

Transmit clears the TX FIFO, clears TX interrupt status, programs retry count, initiator, destination, opcode, operands, and operand count. IRQ handling acknowledges both CEC status registers, reports transmit success or NACK/max-retry completion through `cec_transmit_done()`, clears TX state, and drains received messages through `cec_received_msg()`.

## State and persistence
CEC state is stored in the Linux `cec_adapter` referenced by `core->adap`, the physical address programmed through `cec_s_phys_addr()`, logical address masks in HDMI CEC CA registers, FIFO contents, interrupt masks, retry count, and CEC clock divider. The adapter persists from HDMI component bind until unbind.

## Dependencies and integration points
The file depends on `hdmi.h` register helpers, HDMI4 core power helpers, wrapper IRQ enable helpers, and the Linux media CEC framework. `hdmi4.c` calls `hdmi4_cec_irq()` from the HDMI core interrupt path and updates physical address after EDID reads or disconnects.

## Risks
CEC is clock and power sensitive: enabling CEC increments HDMI core power and must disable the divider and core on failure. FIFO-clear loops are bounded by retry counts but do not sleep, so bad hardware state can return `-EIO`. Receive length is clamped to fit `CEC_MAX_MSG_SIZE`, but malformed FIFO state can still discard frames. The transmit path returns immediately after programming hardware, relying on IRQ completion; lost IRQs would stall framework completion.

## Test signals
Useful signals include adapter registration, enabling/disabling CEC via userspace, logical address programming, physical address updates after EDID and disconnect, successful ping and opcode transmission, NACK/max-retry reporting, received message delivery, CEC clock divider programming, and operation across HDMI hotplug and display power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h

## Purpose
`hdmi4_cec.h` is the conditional private interface between the OMAP4 HDMI bridge driver and the HDMI4 CEC implementation. It exposes CEC init, uninit, IRQ, and physical-address update functions when CEC support is enabled, and no-op stubs when `CONFIG_OMAP4_DSS_HDMI_CEC` is disabled.

## Important APIs, types, and functions
The enabled declarations are `hdmi4_cec_set_phys_addr()`, `hdmi4_cec_irq()`, `hdmi4_cec_init()`, and `hdmi4_cec_uninit()`. The disabled branch provides inline no-op or success-returning versions with the same signatures. Forward declarations cover `struct hdmi_core_data`, `struct hdmi_wp_data`, and `struct platform_device`.

## Control flow
`hdmi4.c` can call the functions unconditionally. With CEC enabled, component bind registers a CEC adapter, IRQ handling dispatches core CEC interrupts, EDID or disconnect updates the CEC physical address, and unbind unregisters the adapter. With CEC disabled, those calls compile away and HDMI display/audio operation is unaffected.

## State and persistence
The header itself has no state. In enabled builds, state lives in `hdmi_core_data::adap` and wrapper/core CEC registers. In disabled builds, no CEC state is created and physical address updates are ignored.

## Dependencies and integration points
The header integrates HDMI4 display code with optional media CEC support while keeping non-CEC builds free of CEC runtime dependencies. It depends on Kconfig to choose declarations versus stubs.

## Risks
No-op stubs make disabled CEC builds easy to support, but tests must explicitly cover enabled builds because compile-time success with CEC disabled does not validate register, IRQ, or adapter logic. Callers must not assume `core->adap` is valid unless CEC initialization has run in an enabled build.

## Test signals
Build both `CONFIG_OMAP4_DSS_HDMI_CEC=y` and disabled configurations. Runtime enabled-build signals include CEC adapter creation, IRQ callback dispatch, physical address changes from EDID, and clean adapter unregister. Disabled-build signals are successful HDMI probe/bind and no unresolved CEC symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_cec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c

## Purpose
`hdmi4_core.c` programs the OMAP4 HDMI core register block. It handles DDC/EDID reads, core video mode setup, AVI infoframe transmission, audio core and infoframe programming, audio start/stop, HDMI core debug dumps, and SoC-specific HDMI4 audio clock feature selection.

## Important APIs, types, and functions
External display functions include `hdmi4_core_ddc_init()`, `hdmi4_core_ddc_read()`, `hdmi4_core_powerdown_disable()`, `hdmi4_configure()`, `hdmi4_core_dump()`, and `hdmi4_core_init()`. Audio functions are `hdmi4_audio_config()`, `hdmi4_audio_start()`, and `hdmi4_audio_stop()`. Internal helpers include `hdmi_core_init()`, software reset assert/release helpers, `hdmi_core_video_config()`, `hdmi_core_write_avi_infoframe()`, `hdmi_core_av_packet_config()`, `hdmi_core_audio_config()`, and `hdmi_core_audio_infoframe_cfg()`.

## Control flow
DDC init enables DDC clocks, aborts any in-progress transaction, clocks SCL devices, and clears the DDC FIFO. DDC read waits for readiness, programs segment, slave address, offset, byte count, and command, checks bus-low and no-ack bits, then reads FIFO bytes with a timeout.

Video configuration initializes wrapper timing and format through common HDMI wrapper helpers, asserts core software reset, configures input bus width, dither/truncation, packet mode, HDMI/DVI mode, TMDS clock selection, releases reset, writes AVI infoframe data when in HDMI mode, and enables repeated AVI/audio packets as needed.

Audio configuration validates IEC/CEA inputs, derives word length and sample frequency, computes ACR N/CTS, chooses software or hardware CTS mode from SoC features, configures I2S, channel layout, DMA/FIFO formatting, IEC channel-status registers, audio infoframe bytes and checksum, and packet generation. Audio start/stop toggles core audio mode and wrapper audio core requests.

## State and persistence
Persistent software state is small: `core->base`, `core->cts_swmode`, `core->audio_use_mclk`, `core->wp`, and `core->adap` from related code. Hardware state is extensive in core system and AV registers: DDC transaction registers, video mode registers, packet control, AVI infoframe bytes, ACR, I2S, IEC channel status, audio layout, audio infoframe, and CEC-visible core state. Values persist until reconfigured, core reset, or power down.

## Dependencies and integration points
The file depends on HDMI4 register definitions from `hdmi4_core.h`, common HDMI wrapper functions from `hdmi.h`, ALSA IEC/CEA structures, DRM HDMI infoframe packing, SoC device matching, and platform resource mapping. `hdmi4.c` calls these routines during EDID reads, bridge enable, and audio callbacks.

## Risks
DDC polling is timeout based and can fail on stuck I2C lines or incomplete aborts. Video configuration assumes RGB/YUV444 24-bit packing and fixed core defaults; unsupported color/deep-color modes are not generalized. Audio mutates the supplied CEA infoframe for multi-channel operation and uses fixed channel mapping. SoC feature matching controls CTS and MCLK behavior; wrong match data can break audio clock recovery. The debug dump reads many registers and must run only while runtime PM keeps the block accessible.

## Test signals
Useful signals include reliable EDID reads for base and extension blocks, no DDC bus-low/no-ack errors with known-good sinks, HDMI and DVI video output, correct AVI infoframes, two-channel and multi-channel LPCM audio, valid ACR N/CTS for 32/44.1/48/96/192 kHz rates, audio start/stop without FIFO faults, debugfs core dumps, and SoC-specific audio behavior on OMAP4430 ES1, ES2, and later OMAP4 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4_core.c -->
