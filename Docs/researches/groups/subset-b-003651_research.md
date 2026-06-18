# subset-b-003651 research

This grouped report covers the requested Qualcomm MSM display driver files. Each section is source-tree aligned and bounded for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.c

Purpose: implements the DPU hardware resource manager. It builds runtime objects for catalog-described blocks and reserves per-CRTC display resources across layer mixers, pingpongs, CTLs, DSPPs, DSCs, CDM, CWB muxes, and SSPPs.

Important APIs and functions: `dpu_rm_init()` instantiates hardware wrappers from `dpu_mdss_cfg`; `dpu_rm_reserve()` drives reservation; `dpu_rm_release()` clears mappings; `dpu_rm_reserve_sspp()` assigns a source pipe by feature need; `dpu_rm_get_assigned_resources()` returns reserved blocks; `dpu_rm_print_state()` dumps mapping state. Internal helpers enforce LM peer selection, PP/DSC parity, legacy CTL split-display requirements, and CWB odd/even mux matching.

Control flow: init walks catalog arrays and stores block pointers in index-by-hardware-id arrays. Reserve first selects LM/PP/DSPP sets, optionally CWB muxes and CWB pingpongs, then CTLs, DSC blocks, and CDM. SSPP reservation is separate and prefers DMA, then RGB, then VIG depending on scale/YUV/rotation requirements.

State and persistence: durable state for commits lives in `struct dpu_global_state` maps from block index to DRM CRTC id. `dpu_rm` itself is a device lifetime catalog cache of block objects. There is no disk persistence.

Dependencies and integration: depends on DPU catalog data, DPU hardware block init helpers, DRM CRTC ids, and DPU atomic global state. Encoders and CRTCs consume assigned resources through `dpu_rm_get_assigned_resources()`. Tracepoints in `dpu_trace.h` expose RM reservation activity.

Risks: partial failure inside `_dpu_rm_make_reservation()` can leave earlier resource map writes unless caller rolls global state back via atomic state abort. Index math assumes catalog ids match array bases. CWB support currently requires dedicated CWB pingpongs. DSC pairing is topology-sensitive and can reject otherwise free blocks because of strict parity.

Test signals: exercise concurrent CRTCs, split display, DSC merge mode, writeback/CWB, YUV CDM, and SSPP feature fallbacks. Debugfs/DRM state should show expected CRTC ids in RM maps, and tracepoints should show LM/CTL reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.h

Purpose: declares the DPU resource manager interface and the topology/requirement structures used by DPU atomic modeset and plane code.

Important APIs and types: `struct dpu_rm` stores arrays of hardware block handles for pingpong, LM, CTL, INTF, WB, CWB, DSPP, merge3d, DSC, SSPP, and CDM. `struct dpu_rm_sspp_requirements` expresses pipe features (`yuv`, `scale`, `rot90`). `struct msm_display_topology` describes requested LM/INTF/DSPP/DSC/CDM counts and CWB enablement. Public functions cover init, reserve, release, SSPP reserve/release, assigned-resource lookup, and state printing. Inline accessors expose INTF/WB/SSPP handles by enum index.

Control flow and integration: callers create `dpu_rm` during KMS init, pass display topologies during atomic reservation, and query assigned blocks while configuring encoders and CRTCs. The header deliberately separates fixed catalog handles in `dpu_rm` from dynamic mappings in `dpu_global_state`.

State and persistence: only declares in-memory objects. Reservation state persists for an atomic global state lifetime, not across driver unload or reboot.

Dependencies: relies on DRM types, `msm_kms.h`, and DPU hardware enum definitions from `dpu_hw_top.h`.

Risks: inline accessors do no bounds checking, so callers must pass valid enum values. The arrays are sized from enum ranges, making catalog enum changes a compatibility point.

Test signals: compile coverage catches signature drift. Runtime tests should verify each accessor returns catalog-created blocks and invalid topologies fail without corrupting `dpu_global_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_trace.h

Purpose: defines the DPU tracepoint surface for performance, IRQ, encoder, CRTC, plane, resource-manager, VBIF, and CTL events. It is the main low-overhead observability layer for this DPU driver code.

Important APIs and events: trace events include `dpu_perf_set_qos_luts`, `dpu_perf_set_danger_luts`, `dpu_perf_set_ot`, `dpu_perf_crtc_update`, IRQ callback register/unregister events, encoder enable/disable/kickoff/RC/wait events, command/video physical encoder events, CRTC mixer/vblank/enable events, plane scanout/disable events, RM LM/CTL/INTF reservation events, VBIF halt failures, external TE connection, core perf clock updates, and CTL pending flush events. `DPU_ATRACE_BEGIN`, `DPU_ATRACE_END`, `DPU_ATRACE_FUNC`, and `DPU_ATRACE_INT` provide Android-style trace markers.

Control flow: the file is included by producers, then `trace/define_trace.h` is included outside the guard as required by Linux tracepoint generation. Event classes reduce repeated definitions for similar payloads.

State and persistence: tracepoints record transient runtime state into kernel tracing buffers when enabled. They do not mutate driver state.

Dependencies and integration: depends on Linux tracepoint macros, DRM rect formatting, and DPU private structs. Users include this header where they call generated `trace_*` functions.

Risks: trace event struct fields dereference caller-provided state; callers must pass valid pointers. Trace payload formats become user-visible diagnostics, so changing fields can disrupt tooling. A few printk payloads repeat the wrong field for video IRQ refcnt, which is a diagnostic accuracy risk.

Test signals: kernel build validates trace macro expansion. Runtime validation comes from enabling `dpu:*` trace events during modeset, vblank, kickoff, VBIF, and RM stress tests and checking coherent ids, masks, and dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.c

Purpose: configures the DPU VBIF bus interface for outstanding transaction limits, QoS remapping, error clearing, memory types, and debugfs exposure.

Important APIs and functions: `dpu_vbif_set_ot_limit()` calculates and programs read/write OT limits; `dpu_vbif_set_qos_remap()` applies real-time or non-real-time QoS priority tables; `dpu_vbif_clear_errors()` clears pending/source error registers; `dpu_vbif_init_memtypes()` programs catalog memory types; `dpu_debugfs_vbif_init()` exposes static catalog parameters in debugfs. Internal `_dpu_vbif_wait_for_xin_halt()` waits for halt acknowledgement, `_dpu_vbif_get_ot_limit()` selects limits, and `_dpu_vbif_apply_dynamic_ot_limit()` adjusts WFD limits based on pixels per second.

Control flow: OT programming optionally enables write-gather, skips no-op writes, traces the chosen limit, writes limit configuration, asserts halt, waits with timeout, traces failure, then deasserts halt. QoS remap loops over catalog priority levels.

State and persistence: state is hardware register state in VBIF; no software persistence beyond catalog pointers. Debugfs files expose read-only or restricted values.

Dependencies and integration: integrates with `struct dpu_kms`, `dpu_hw_vbif` ops, catalog VBIF tables, debugfs, and DPU performance/plane paths that compute client parameters.

Risks: halt wait blocks up to catalog timeout and can delay atomic work. Bad catalog defaults can skip needed programming or overconstrain bus traffic. Dynamic OT only applies to WFD paths. Missing ops cause silent no-op behavior except debug logs.

Test signals: validate display and writeback stability under high bandwidth, confirm VBIF tracepoints show expected OT changes, force timeout paths with faulty hardware simulation, and inspect debugfs values against catalog.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.h

Purpose: declares parameter structures and public functions for DPU VBIF programming.

Important APIs and types: `struct dpu_vbif_set_ot_params` carries XIN id, pipe/debug number, dimensions, frame rate, read/write direction, and WFD marker. `struct dpu_vbif_set_memtype_params` describes a XIN/cacheability pair but is not consumed by the adjacent implementation. `struct dpu_vbif_set_qos_params` carries XIN id, debug pipe number, and real-time classification. Public functions configure OT limits, QoS remap, error clearing, memtype initialization, and debugfs setup.

Control flow and integration: DPU plane/performance code can assemble OT and QoS parameters for each hardware client and call into `dpu_vbif.c`; KMS init can call memory type setup and debugfs registration.

State and persistence: the header has no state; hardware register persistence is managed by the implementation and lost on reset or power cycle.

Dependencies: includes `dpu_kms.h`, so users get DPU KMS and catalog types. Debugfs prototype assumes `struct dentry` visibility through included headers or compile context.

Risks: parameter structs must stay aligned with hardware ops and catalog interpretation. Width, height, and frame-rate values directly affect dynamic OT choice, so stale or zero values can underprogram bus limits.

Test signals: compile tests for all users, plus runtime coverage for read and write clients, WFD paths, and RT/NRT QoS table selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.c

Purpose: creates and validates a DRM writeback connector for DPU writeback encoders.

Important APIs and functions: `dpu_writeback_init()` allocates `struct dpu_wb_connector`, installs connector helper funcs, and calls `drmm_writeback_connector_init()`. `dpu_wb_conn_get_modes()` creates no-EDID modes bounded by catalog `max_mixer_width` and DRM `max_height`. `dpu_wb_conn_atomic_check()` validates writeback job framebuffer dimensions against the CRTC mode, enforces `maxlinewidth`, and only accepts linear modifiers. `dpu_wb_conn_prepare_job()` and `dpu_wb_conn_cleanup_job()` delegate framebuffer job setup/teardown to DPU encoder helpers.

Control flow: atomic check is a no-op for disconnected or job-less states, otherwise it obtains CRTC state, compares job framebuffer to mode, and then invokes DRM writeback helper validation. Job callbacks skip null framebuffers.

State and persistence: connector state is managed by DRM atomic helpers. The DPU wrapper stores the encoder pointer and max line width for the connector lifetime.

Dependencies and integration: depends on DRM writeback helpers, DPU KMS catalog, and `dpu_encoder_prepare_wb_job()`/`dpu_encoder_cleanup_wb_job()`. Writeback resource reservation is handled elsewhere by DPU RM and encoder code.

Risks: modes are limited to mixer width until dual-SSPP/source split support exists, so some valid hardware writeback combinations may be hidden. Non-linear modifiers are rejected. Incorrect max height or catalog max line width can expose modes that later fail bandwidth checks.

Test signals: atomic writeback jobs should pass only when framebuffer size equals mode, width is within max line width, and modifier is linear. IGT writeback and invalid-fb tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.h

Purpose: declares the DPU-specific DRM writeback connector wrapper and init entry point.

Important APIs and types: `struct dpu_wb_connector` embeds `struct drm_writeback_connector`, tracks the associated writeback encoder in `wb_enc`, and stores `maxlinewidth`. `to_dpu_wb_conn()` converts from the embedded DRM writeback connector to the wrapper. `dpu_writeback_init()` constructs the connector for an encoder and format list.

Control flow and integration: DPU KMS or encoder initialization uses `dpu_writeback_init()` after creating a writeback encoder. DRM writeback callbacks installed in the C file then route job preparation and cleanup back to the DPU encoder.

State and persistence: all state is in-memory DRM object lifetime state. The wrapper has no persistent storage.

Dependencies: includes DRM CRTC/file/probe/writeback headers and DPU/MSM driver headers. It relies on `dpu_encoder_phys.h` for encoder-side writeback job hooks.

Risks: the container conversion assumes callers pass a `drm_writeback_connector` embedded in `dpu_wb_connector`. The encoder pointer must remain valid for the connector lifetime.

Test signals: compile coverage for DRM API signature changes, writeback connector creation tests, and writeback job execution/cleanup under normal and aborted atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_writeback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_crtc.c

Purpose: implements MDP4 DRM CRTC objects, including mixer setup, overlay flush, vblank event completion, legacy hardware cursor handling, and CRTC IRQ callbacks.

Important APIs and functions: `mdp4_crtc_init()` constructs a CRTC for a DMA/overlay pair. Atomic helpers include mode set, enable, disable, check, begin, and flush. Public helpers `mdp4_crtc_set_config()`, `mdp4_crtc_set_intf()`, and `mdp4_crtc_wait_for_commit_done()` are used by encoders and KMS commit flow. Cursor entry points are `mdp4_crtc_cursor_set()` and `mdp4_crtc_cursor_move()`.

Control flow: atomic flush stores any DRM event, programs blend/mixer state, writes overlay flush bits, and requests a vblank IRQ. The vblank callback unregisters its one-shot IRQ, atomically consumes pending cursor/flip flags, sends flip events, updates cursor registers, and schedules old cursor GEM unpin on a workqueue.

State and persistence: `struct mdp4_crtc` tracks enabled state, DMA/overlay routing, pending event, last flush mask, cursor BOs/iovas, and IRQ descriptors. State is volatile hardware and in-memory DRM state.

Dependencies and integration: uses MDP IRQ helpers, DRM vblank/event locks, MSM GEM IOVA pinning, MDP4 register helpers, and plane pipe ids. Encoders call into CRTC config/intf functions to route output.

Risks: cursor register updates are intentionally vblank-only to avoid underflow, so missed vblank can delay cursor changes. `atomic_check()` is minimal, leaving validation to planes/encoders. Mixer setup scans all CRTCs without explicit extra locking.

Test signals: page flip event timing, cursor set/move/disable, vblank enable/disable, underrun recovery, and flush wait timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dsi_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dsi_encoder.c

Purpose: implements the MDP4 encoder path for DSI video output when `CONFIG_DRM_MSM_DSI` is enabled.

Important APIs and functions: `mdp4_dsi_encoder_init()` allocates a DRM DSI encoder and installs helper callbacks. `mdp4_dsi_encoder_mode_set()` programs DSI timing registers from the adjusted mode. `mdp4_dsi_encoder_enable()` programs DMA packing/dither config, routes the CRTC to `INTF_DSI_VIDEO`, enables DSI output, and marks the encoder enabled. `mdp4_dsi_encoder_disable()` disables output and waits for primary vsync so the disable latches.

Control flow: modeset derives horizontal/vertical timing values, polarity, display start/end, and underflow recovery color. Enable uses CRTC helpers to program output format and interface selection before setting `REG_MDP4_DSI_ENABLE`. Disable is guarded by the local enabled flag and waits on `MDP4_IRQ_PRIMARY_VSYNC`.

State and persistence: state is a boolean `enabled` in the encoder plus programmed MDP4 DSI registers. No persistent storage.

Dependencies and integration: integrates with MDP4 KMS register helpers, MDP IRQ wait, DRM encoder helpers, and MSM DSI modeset attachment performed in `mdp4_kms.c`.

Risks: only video mode is used here; DSI command mode is not represented. Timing polarity and skew contain TODOs for panel-provided values. Disable depends on a functioning primary vblank source.

Test signals: DSI panel modeset, enable/disable cycles, suspend/resume, underflow behavior, and verifying timing registers against adjusted modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dsi_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dtv_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dtv_encoder.c

Purpose: implements the MDP4 TMDS/DTV encoder used for HDMI-style external output.

Important APIs and functions: `mdp4_dtv_encoder_init()` allocates the encoder and obtains `hdmi_clk` and `tv_clk`. `mdp4_dtv_encoder_mode_set()` stores pixel clock and programs DTV timing/polarity registers. `mdp4_dtv_encoder_enable()` routes the CRTC to external mixer/interface, sets and enables clocks, enables DTV output, and flips the enabled flag. `mdp4_dtv_encoder_disable()` disables DTV output, waits for external vsync, disables clocks, and clears state. `mdp4_dtv_round_pixclk()` delegates clock rounding to `tv_clk`.

Control flow: enable first configures the DMA pack format and CRTC routing, then applies pixel clock rate and enables both MDP TV and HDMI clocks before asserting `REG_MDP4_DTV_ENABLE`.

State and persistence: stores pixel clock, clock handles, and `enabled`; hardware register state is volatile.

Dependencies and integration: used by `mdp4_kms.c` for TMDS interface setup and HDMI bridge/connector init. Depends on clock framework, DRM encoder helpers, MDP IRQ waits, and MDP4 register helpers.

Risks: clock enable failures are logged but do not unwind earlier clock actions or abort enable. Disable warns if called while not enabled. Polarity/skew are mode-derived with TODOs for panel/connector data.

Test signals: HDMI hotplug/modeset, pixel clock rounding, repeated enable/disable, external vblank wait, and underrun clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_dtv_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_irq.c

Purpose: provides MDP4 interrupt mask programming, install/uninstall hooks, top-level IRQ dispatch, vblank mask control, and underrun error reporting.

Important APIs and functions: `mdp4_set_irqmask()` writes clear and enable registers; `mdp4_irq_preinstall()` clears/disables interrupts; `mdp4_irq_postinstall()` registers the underrun error handler; `mdp4_irq_uninstall()` disables interrupts; `mdp4_irq()` reads enabled status, clears handled bits, dispatches MDP callbacks, and notifies DRM vblank; `mdp4_enable_vblank()` and `mdp4_disable_vblank()` update the MDP vblank mask.

Control flow: the IRQ handler masks raw status with enabled bits, clears those bits, lets the shared MDP dispatcher invoke registered `mdp_irq` callbacks, then loops CRTCs to call `drm_crtc_handle_vblank()` for matching CRTC vblank masks.

State and persistence: hardware interrupt enable/clear registers and shared MDP IRQ registration state. The file itself keeps no persistent state except static ratelimit state in the error handler.

Dependencies and integration: integrates with `mdp_kms` IRQ registration, DRM vblank core, `mdp4_crtc_vblank()`, and optional global `dumpstate` for ratelimited state dumps.

Risks: top-level handler always returns `IRQ_HANDLED`, even if no enabled status bits were active. Vblank mask updates temporarily enable clocks around register access. Error reporting is ratelimited, which can hide frequent underrun details.

Test signals: interrupt install/uninstall, vblank enable/disable, page flip completion, underrun injection, and dumpstate-triggered DRM state dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.c

Purpose: owns MDP4 KMS platform setup, hardware initialization, modeset object construction, power/clock control, VM setup, and platform driver registration.

Important APIs and functions: `mdp4_probe()` maps registers, gets IRQ/regulator/clocks, and invokes `msm_drv_probe()`. `mdp4_kms_init()` initializes `mdp_kms`, validates hardware revision, enables runtime PM, disables bootloader-left outputs, initializes VM and modeset objects, and allocates/pins a blank cursor BO. `modeset_init()` creates planes, CRTCs, and LVDS/DSI/TMDS interfaces. `mdp4_hw_init()` programs fetch, portmap, layer mixer, and default CSC/operation registers. `mdp4_enable()` and `mdp4_disable()` gate core/interface/LUT/AXI clocks.

Control flow: probe collects platform resources, then DRM component init calls KMS init. KMS init programs clocks and revision checks before object creation. Commit hooks enable/disable clocks and wait for per-CRTC flush completion.

State and persistence: `struct mdp4_kms` stores device, revision, mmio, clocks, regulator, IRQ handler, runtime PM flag, and blank cursor BO/iova. No disk persistence.

Dependencies and integration: integrates DRM bridges/connectors for LVDS, HDMI, and DSI; MSM GEM/VM; runtime PM; clock/regulator frameworks; and MDP shared KMS ops.

Risks: limited fixed topology: two CRTCs and fixed RGB/VG plane assumptions. Some optional clock/regulator handling relies on bootloader/platform behavior. Failure paths call `mdp4_destroy()` if `kms` exists, so partially initialized resources must tolerate cleanup.

Test signals: probe/remove, revision mismatch, modeset init per interface, blank cursor allocation, suspend/resume, and bootloader-enabled-output cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.h

Purpose: central private header for MDP4 KMS structures, register accessors, bit translation helpers, and cross-file prototypes.

Important APIs and types: `struct mdp4_kms` embeds `mdp_kms` and stores DRM device, revision, MMIO, regulator, clocks, error handler, runtime PM flag, and blank cursor BO/iova. Inline helpers wrap MMIO reads/writes and translate pipes, overlays, DMAs, and mixer stage selections into hardware bit masks. `mdp4_pipe_caps()` exposes plane feature caps by pipe class.

Control flow and integration: CRTC, plane, encoder, IRQ, PLL, and KMS files include this header to share MDP4 register layout helpers and function prototypes. Encoders call CRTC config/routing helpers declared here.

State and persistence: declares in-memory KMS state only. Hardware register state is managed by users of `mdp4_write()` and `mdp4_read()`.

Dependencies: includes DRM panel, MSM driver/KMS, shared `mdp_kms`, and generated `mdp4.xml.h` register definitions.

Risks: helper mappings must match hardware bit definitions; invalid enum values generally map to zero, which can silently skip flush or IRQ bits. `mixercfg()` warns for invalid pipes but still returns current config.

Test signals: build coverage after generated register updates, per-pipe flush/IRQ validation, and modeset tests proving expected pipe-to-mixer routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lcdc_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lcdc_encoder.c

Purpose: implements the MDP4 LVDS/LCDC encoder path, including LCDC timing, LVDS PHY mux programming, clock/regulator control, and mode validation.

Important APIs and functions: `mdp4_lcdc_encoder_init()` allocates an LVDS encoder, obtains the LCDC clock through `mdp4_get_lcdc_clock()`, and gets LVDS regulators. `mdp4_lcdc_encoder_mode_set()` programs LCDC timing registers and stores pixel clock. `mdp4_lcdc_encoder_enable()` programs DMA output format, routes the CRTC, enables regulators and LCDC clock, configures the LVDS PHY, enables LCDC, and marks enabled. `mdp4_lcdc_encoder_disable()` disables LCDC, waits for primary vsync, disables clock/regulators, and clears enabled. `mdp4_lcdc_encoder_mode_valid()` requires exact clock rounding.

Control flow: `setup_phy()` derives bits per pixel from connector display info, falls back to 18 bpp, writes 18/24-bit LVDS mux tables, lane enables, PHY config, and serialization enable after a short delay.

State and persistence: stores LCDC clock, pixel clock, regulator handles, and enabled flag. Register and regulator states are volatile.

Dependencies and integration: depends on DRM connector display info, MDP4 CRTC routing, LVDS PLL helper, regulator framework, and clock framework.

Risks: LVDS channel count, swap, and some data-enable polarity are hard-coded/TODO. Unsupported bpp aborts PHY setup after earlier enable work. Exact clock validation can reject modes a panel might tolerate.

Test signals: LVDS panel modes, 18/24 bpp paths, regulator failures, exact clock validation, enable/disable latch wait, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lcdc_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lvds_pll.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lvds_pll.c

Purpose: registers a simple LVDS PLL clock provider for MDP4 LCDC/LVDS output.

Important APIs and functions: `mdp4_get_lcdc_clock()` initializes the PLL and returns the platform `lcdc_clk` if present, otherwise returns the PLL clock directly. `mdp4_lvds_pll_init()` allocates/registers `clk_hw` and OF clock provider. Clock ops implement enable, disable, recalc, determine_rate, and set_rate. `find_rate()` selects an entry from a static frequency table.

Control flow: set_rate stores requested pixel clock. enable selects the nearest configured table entry, resets the LVDS PHY, writes PLL control registers, enables PLL control, then busy-waits for the lock bit. disable clears PHY and PLL control registers.

State and persistence: `struct mdp4_lvds_pll` stores DRM device and selected pixel clock. Hardware PLL state persists only while powered/enabled.

Dependencies and integration: used by LCDC encoder init. Depends on clock provider APIs, OF clock registration, MDP4 MMIO helpers, and generated LVDS PHY registers.

Risks: the frequency table contains only one configured rate, so clock selection is very limited. The lock wait has no timeout and can spin forever on broken hardware. `find_rate()` assumes a non-empty sorted table.

Test signals: clock registration, fallback when `lcdc_clk` is missing, rate determination, PLL lock on hardware, and disable clearing PHY/PLL state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_lvds_pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_plane.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_plane.c

Purpose: implements MDP4 DRM planes, framebuffer preparation/cleanup, scanout programming, scaling checks, format setup, CSC setup for YUV, and plane creation.

Important APIs and functions: `mdp4_plane_init()` creates primary or overlay planes with RGB or RGB+YUV formats based on pipe caps. `mdp4_plane_atomic_update()` calls `mdp4_plane_mode_set()`. `mdp4_plane_prepare_fb()` and cleanup pin/unpin framebuffer backing through MSM helpers. `mdp4_plane_set_scanout()` writes per-plane strides and IOVA bases. `mdp4_write_csc_config()` writes CSC matrix/bias/clamp registers.

Control flow: mode_set ignores disabled plane states, converts source rectangles from Q16 to integer pixels, checks up/down scaling limits, sets scaling op bits and phase steps, writes source/destination geometry, framebuffer addresses, source format/unpack fields, optional YUV CSC state, op mode, phase steps, and tiled frame size when needed.

State and persistence: each plane stores pipe id and name. Framebuffer pinning state is managed by MSM framebuffer helpers. Hardware register state is volatile and latched by CRTC flush.

Dependencies and integration: integrates with DRM atomic helpers, damage clips, MSM format descriptors, MDP4 register helpers, and CRTC flush/mixer configuration.

Risks: `atomic_check()` is empty, so invalid scaling or format combinations fail late in atomic update with `WARN_ON`. Property helpers are placeholders. Tiled support is narrow and tied to Samsung 64x32 NV12.

Test signals: RGB and YUV scanout, NV12 tiled modifier, scaling limit failures, framebuffer pin cleanup, damage clip support, and blend interactions with CRTC mixer setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp4/mdp4_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.c

Purpose: provides static hardware configuration tables for many MDP5 revisions and selects the active configuration at KMS init.

Important APIs and functions: `mdp5_cfg_init()` chooses a config by major/minor revision, sets the global `mdp5_cfg`, and returns a handler. `mdp5_cfg_get_hw_config()`, `mdp5_cfg_get_config()`, and `mdp5_cfg_get_hw_rev()` expose selected data. Static `mdp5_cfg_hw` entries describe block counts, register bases, capabilities, SMP layout, CTL flush masks, layer mixers, pingpongs, DSPPs, CDM/DSC, interfaces, performance inefficiency factors, and max clock for chip families such as msm8x26, msm8x74, apq8084, msm8x16, msm8x36, msm8x94, msm8x96, msm8x76, msm8x53, msm8917, and msm8937.

Control flow: `mdp5_cfg_init()` allocates a handler, selects the revision table for major version 1, searches for matching minor revision, publishes the global pointer, and stores revision/config in the handler.

State and persistence: all tables are static const data; selected handler is devm-managed. The global `mdp5_cfg` is runtime global state used by generated register helpers.

Dependencies and integration: used by MDP5 KMS, CTL manager, mixer, SMP, plane, and generated `mdp5.xml.h` offset logic.

Risks: the global pointer means only one active MDP5 config is represented process-wide. Incorrect table values cause bad register offsets, resource counts, or flush masks. Unsupported revisions fail probe.

Test signals: probe each supported revision, verify config name/log, register offsets, CTL/mixer/plane counts, interface mappings, and max clock/perf behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.h

Purpose: declares the MDP5 hardware configuration data model and selection API.

Important APIs and types: `struct mdp5_cfg_hw` aggregates MDP caps, SMP layout, CTL layout, VIG/RGB/DMA/cursor pipe blocks, LM instances, DSPP/AD/PP/DSC/CDM/WB blocks, interface connections, performance factors, and max clock. Supporting types define common sub-blocks, LM instances, pipe caps, CTL flush masks, SMP reserved state, writeback instances, and interface base/connect arrays. `mdp5_cfg_init()` and getter functions expose selected config. The `mdp5_cfg_intf_is_virtual()` macro classifies virtual interfaces such as writeback.

Control flow and integration: MDP5 init calls `mdp5_cfg_init()` after reading hardware version. Other modules query the handler to size pools, assign resources, compute flush masks, and program interfaces.

State and persistence: header declares extern global `mdp5_cfg`, but no storage. Config data is static and runtime-selected.

Dependencies: includes MSM driver types and generated enum/cap definitions available through display headers.

Risks: fixed maximums (`MAX_CTL`, `MAX_BASES`, `MAX_SMP_BLOCKS`, `MAX_CLIENTS`) must cover all tables. The virtual interface macro evaluates its argument once but depends on enum ordering.

Test signals: compile coverage for table initializers, probe coverage for each revision, resource manager bounds checks, and tests that generated register access uses selected bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cmd_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cmd_encoder.c

Purpose: implements MDP5 DSI command-mode encoder support, centered on pingpong tearcheck and CTL start signaling.

Important APIs and functions: `mdp5_cmd_encoder_mode_set()` programs tearcheck for the adjusted mode and sets the CRTC pipeline. `mdp5_cmd_encoder_enable()` enables tearcheck, flushes encoder timing bits through CTL, marks encoder state enabled, and sets the local enabled flag. `mdp5_cmd_encoder_disable()` disables tearcheck, marks encoder state disabled, commits encoder flush, and clears enabled. Internal helpers set up, enable, and disable pingpong tearcheck using `vsync_clk`.

Control flow: tearcheck setup gets the active mixer pingpong id, rounds `vsync_clk` to 19.2 MHz, computes clocks per line from vtotal and refresh, writes sync config, height, init, read pointer IRQ, start position, thresholds, and disables autorefresh. Enable sets/enables the clock and asserts `PP_TEAR_CHECK_EN`.

State and persistence: state is the shared `struct mdp5_encoder` enabled flag and hardware pingpong/clock registers. No file-local persistent state.

Dependencies and integration: only compiled with DSI support. Depends on MDP5 CRTC pipeline/mixer helpers, CTL commit/state APIs, clock framework, and pingpong registers.

Risks: if `vsync_clk` is missing or cannot round/enable, command-mode enable fails. The fallback tearcheck cadence is approximate and documented as a stability fallback because panel interrupts are not wired.

Test signals: DSI command-mode panel commits, pp_done completion, vsync clock error paths, enable/disable cycles, and tearcheck register programming against mode refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_cmd_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_crtc.c

Purpose: implements MDP5 DRM CRTCs, including dynamic mixer assignment, stage/zpos validation, blending, flush/start sequencing, command-mode pp_done waits, vblank/event handling, scanout position, vblank counter, and legacy LM cursor support.

Important APIs and functions: `mdp5_crtc_init()` constructs CRTCs. Atomic helpers include custom state reset/duplicate/destroy/print, mode_set, check, flush, enable, and disable. Public helpers expose vblank mask, pipeline setup, CTL/mixer/pipeline access, and commit wait. Cursor functions support legacy LM cursors when no cursor plane is provided.

Control flow: atomic check collects visible planes, marks command-mode dirtyfb needs, decides whether a right mixer is needed for source split or wide modes, assigns/release mixers, computes IRQ masks, sorts planes by zpos, and assigns mixer stages. Atomic flush stores page-flip event, programs blend state through LM registers and CTL layer regs, arms pp_done for command mode, commits all flush bits, updates IRQ masks, and requests one-shot vblank completion. Commit wait uses pp_done for command mode and flush register drain for video mode.

State and persistence: `struct mdp5_crtc` stores enabled state, event, flush mask, pending flags, IRQ descriptors, pp completion, cursor BO/iova/dimensions/position, and LM lock. `mdp5_crtc_state` stores CTL and pipeline.

Dependencies and integration: depends on MDP5 CTL, mixer assignment, plane flush/pipe helpers, encoder line/frame counters, DRM vblank/event core, MSM GEM, runtime PM, and MDP IRQ dispatch.

Risks: legacy LM cursor is unsupported with source split and deprecated when cursor planes exist. Mixer assignment and release happen during atomic check and must stay consistent with DRM atomic state rollback. Stage count and fullscreen assumptions determine whether border color is required.

Test signals: multi-plane zpos, cursor plane versus LM cursor, source split, command-mode pp_done waits, video flush waits, vblank timestamp/counter, suspend/resume cursor restore, and invalid too-many-plane commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.c

Purpose: implements the MDP5 CTL pool manager and CTL programming layer. CTLs describe and flush display pipelines shared by interfaces.

Important APIs and functions: `mdp5_ctlm_init()` creates the CTL pool from hardware config; `mdp5_ctlm_request()` allocates a CTL, preferring booked CTLs for DSI interface numbers 1/2; `mdp5_ctlm_hw_reset()` clears CTL ops. CTL APIs set pipeline/interface selection, encoder state, cursor routing, layer blending, flush masks, commit/start, commit status, and CTL id.

Control flow: `mdp5_ctl_set_pipeline()` programs display interface selection and CTL op bits for command mode, writeback line mode, and 3D packing/source split. `mdp5_ctl_blend()` resets layer registers, builds left/right mixer layer and extension masks from stage arrays, preserves cursor output, writes layer regs, and records pending CTL trigger bits. `mdp5_ctl_commit()` adds CTL flush when pending trigger bits overlap, applies software flush fixes for targets without dedicated bits, filters by hardware mask, accumulates if `start` is false, otherwise writes flush register and sends START when needed.

State and persistence: each `mdp5_ctl` tracks id, busy/booked status, encoder enabled, accumulated flush mask, hw lock, register offset, pending trigger bits, and cursor state. Pool state is protected by `pool_lock`.

Dependencies and integration: used by MDP5 CRTC and encoder paths; depends on MDP5 config flush masks, interface structs, pipeline structs, and MDP5 register helpers.

Risks: allocated CTLs are marked busy but this file does not show a release API, so lifecycle is controlled elsewhere or persistent per encoder. Flush mask filtering can hide missing config bits if tables are wrong. `stage_cnt` loop relies on initialized stage arrays.

Test signals: CTL allocation exhaustion, DSI command START, writeback START, cursor enable/disable flush, source split blending, deferred start modesets, and targets with shared cursor/LM flush bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.h

Purpose: declares the MDP5 CTL manager and CTL programming API used by MDP5 CRTCs, encoders, and pipeline setup code.

Important APIs and types: opaque `struct mdp5_ctl_manager` and `struct mdp5_ctl` enforce encapsulation. Manager functions initialize the pool, reset hardware, and request a CTL for an interface. CTL functions get CTL id, set pipeline, set encoder state, route cursor, program blend layers, compute flush masks for LM/pipe/cursor/encoder, commit flush/start, and read commit status. `MAX_PIPE_STAGE` defines left/right pipe slots per stage, and `MDP5_CTL_BLEND_OP_FLAG_BORDER_OUT` requests border color base output.

Control flow and integration: atomic encoder check places a CTL into CRTC state; CRTC blend and flush code then calls the functions declared here. Encoder enable/disable uses encoder flush masks and encoder state updates.

State and persistence: no state in the header; opaque objects are allocated in `mdp5_ctl.c`.

Dependencies: includes MSM driver definitions and relies on MDP5 enum types for pipes and interfaces.

Risks: API callers must provide a valid pipeline with mixer/interface and stage arrays sized to `STAGE_MAX + 1` by `MAX_PIPE_STAGE`. No release prototype appears here, so CTL ownership semantics are not obvious from this file alone.

Test signals: compile coverage, CTL allocation and pipeline setup during modesets, flush mask correctness for every pipe/interface, and debug state showing expected CTL ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_encoder.c

Purpose: implements generic MDP5 DRM encoder logic for video-mode interfaces and dispatches to command-mode DSI helpers when needed.

Important APIs and functions: `mdp5_encoder_init()` allocates an encoder, stores its interface and CTL, initializes interface lock, and installs helpers. `mdp5_encoder_atomic_check()` connects CTL/interface into CRTC state and marks deferred start for modesets. `mdp5_encoder_enable()`, disable, and mode_set dispatch based on interface mode. Video-mode helpers program interface timing, panel format, frame/line counters, enable/disable timing engine, flush encoder bits, wait for disable latch, and update encoder state. Accessors return line count, frame count, and set DSI command/video mode.

Control flow: video mode_set derives sync/display windows and panel format from connector bpc, writes INTF registers under lock, and calls `mdp5_crtc_set_pipeline()`. Enable reprograms mode from current CRTC state, enables timing engine, commits encoder flush, and marks encoder state enabled. Disable clears timing engine, commits, waits for vblank, and marks disabled.

State and persistence: `struct mdp5_encoder` stores CTL, interface, enabled flag, and lock. Hardware timing register state is volatile.

Dependencies and integration: integrates with DRM encoder helpers, MDP5 CRTC pipeline, CTL commit/state, DSI command encoder helpers, interface IRQ helpers, and connector display info.

Risks: enable calls mode_set itself, so ordering with full modeset/deferred start is delicate. DSI cannot handle active-low sync, so polarity handling differs by interface. Connector bpc defaults to 8 when unknown.

Test signals: HDMI/eDP/DSI video modes, DSI command mode switch, full modeset versus plane-only commits, vblank latch wait, frame/line counters, and panel bpc variations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_irq.c

Purpose: implements MDP5 interrupt mask programming, install/uninstall hooks, top-level interrupt dispatch, vblank mask control, and underrun error reporting.

Important APIs and functions: `mdp5_set_irqmask()` writes interrupt clear and enable registers; `mdp5_irq_preinstall()` clears/disables interrupts under runtime PM; `mdp5_irq_postinstall()` registers underrun error handling; `mdp5_irq_uninstall()` disables interrupts; `mdp5_irq()` clears active enabled status, dispatches registered MDP IRQ callbacks, and notifies DRM vblank for matching CRTCs; `mdp5_enable_vblank()` and `mdp5_disable_vblank()` update the shared vblank mask under runtime PM.

Control flow: pre/post/uninstall wrap register access in `pm_runtime_get_sync()`/`put_sync()`. The IRQ handler reads enabled and status registers without explicit PM wrapping because it runs for active hardware, clears status, calls `mdp_dispatch_irqs()`, then calls `drm_crtc_handle_vblank()` for CRTCs whose current vblank mask matches.

State and persistence: hardware interrupt enable/status registers and shared MDP IRQ registration state. Static ratelimit state throttles optional dump output.

Dependencies and integration: used by MDP5 KMS ops, CRTC vblank/pp_done/error callbacks, DRM vblank core, runtime PM, and optional global `dumpstate`.

Risks: always returns `IRQ_HANDLED`; spurious IRQ accounting is not exposed. If runtime PM state is inconsistent, mask updates can fail or race. Ratelimited error logs may hide repeated underruns.

Test signals: vblank enable/disable, page flip completion, command-mode pp_done delivery through dispatch, underrun injection, suspend/resume mask restore, and dumpstate-triggered DRM state dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_irq.c -->
