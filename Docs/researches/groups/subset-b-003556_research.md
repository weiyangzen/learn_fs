# subset-b-003556 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper.c

### Purpose
`drm_dp_helper.c` is the DRM display helper implementation for common DisplayPort and embedded DisplayPort behavior. It provides exported helper APIs for link-training status decoding, AUX/DPCD transfer retries, I2C-over-AUX, MST payload table updates, downstream branch and protocol-converter capability parsing, sink and LTTPR descriptors, DSC capability math, VSC/adaptive-sync SDP handling, PCON HDMI FRL/DSC control, eDP AUX backlight control, panel backlight registration, CRC capture, and bandwidth-overhead calculations.

The file is deliberately central rather than driver-specific: GPU drivers, bridge drivers, MST topology code, panels, and debug paths use these helpers so they do not each reimplement DP register layouts, DPCD retry behavior, or VESA timing formulas.

### Important APIs, Types, And Functions
The local `struct dp_aux_backlight` binds a registered `backlight_device`, the `drm_dp_aux` transport, parsed `drm_edp_backlight_info`, and an enable flag for panel-managed AUX backlight operation.

Link-training status helpers include `drm_dp_channel_eq_ok()`, `drm_dp_clock_recovery_ok()`, `drm_dp_post_lt_adj_req_in_progress()`, `drm_dp_get_adjust_request_voltage()`, `drm_dp_get_adjust_request_pre_emphasis()`, `drm_dp_get_adjust_tx_ffe_preset()`, and DP 2.x 128b/132b helpers such as `drm_dp_128b132b_lane_channel_eq_done()`, `drm_dp_128b132b_lane_symbol_locked()`, `drm_dp_128b132b_eq_interlane_align_done()`, `drm_dp_128b132b_cds_interlane_align_done()`, and `drm_dp_128b132b_link_training_failed()`. These parse the six-byte link status block returned from DPCD lane-status registers.

Training delay helpers include `drm_dp_read_clock_recovery_delay()`, `drm_dp_read_channel_eq_delay()`, `drm_dp_128b132b_read_aux_rd_interval()`, `drm_dp_link_train_clock_recovery_delay()`, `drm_dp_link_train_channel_eq_delay()`, `drm_dp_lttpr_link_train_clock_recovery_delay()`, and `drm_dp_lttpr_link_train_channel_eq_delay()`. Internally they select between 8b/10b, 128b/132b, DPRX, and LTTPR register encodings, with defaults when reads fail.

Core AUX and DPCD APIs include `drm_dp_dpcd_probe()`, `drm_dp_dpcd_set_powered()`, `drm_dp_dpcd_set_probe()`, `drm_dp_dpcd_read()`, `drm_dp_dpcd_write()`, `drm_dp_dpcd_read_link_status()`, `drm_dp_dpcd_read_phy_link_status()`, `drm_dp_link_power_up()`, and `drm_dp_link_power_down()`. `drm_dp_dpcd_access()` is the key private native-AUX retry loop and uses `aux->transfer()`, `aux->hw_mutex`, `aux->powered_down`, and native reply decoding.

MST payload helpers include `drm_dp_dpcd_write_payload()`, `drm_dp_dpcd_clear_payload()`, and `drm_dp_dpcd_poll_act_handled()`. They manipulate `DP_PAYLOAD_ALLOCATE_SET` and `DP_PAYLOAD_TABLE_UPDATE_STATUS` and poll for sink/hub acknowledgement.

Downstream branch helpers include `drm_dp_read_dpcd_caps()`, `drm_dp_read_downstream_info()`, `drm_dp_downstream_is_type()`, `drm_dp_downstream_is_tmds()`, `drm_dp_send_real_edid_checksum()`, max/min TMDS and dot-clock helpers, max-bpc and color-conversion helpers, `drm_dp_downstream_mode()`, `drm_dp_downstream_id()`, `drm_dp_downstream_debug()`, `drm_dp_subconnector_type()`, `drm_dp_set_subconnector_property()`, `drm_dp_read_sink_count_cap()`, and `drm_dp_read_sink_count()`. These are used by connector detection, debugfs reporting, and mode validation.

I2C-over-AUX support is implemented through `drm_dp_i2c_xfer()`, `drm_dp_i2c_do_msg()`, `drm_dp_i2c_drain_msg()`, the `drm_dp_i2c_algo` algorithm, and `drm_dp_i2c_lock_ops`. Module parameters `dp_aux_i2c_speed_khz` and `dp_aux_i2c_transfer_size` tune retry estimates and transaction chunking.

AUX lifecycle and userspace-facing registration helpers are `drm_dp_remote_aux_init()`, `drm_dp_aux_init()`, `drm_dp_aux_register()`, and `drm_dp_aux_unregister()`. They initialize mutexes, CEC lock state, CRC work, the I2C adapter, and optional AUX char-device nodes via `drm_dp_helper_internal.h`.

CRC and PSR helpers include `drm_dp_start_crc()`, `drm_dp_stop_crc()`, `drm_dp_aux_crc_work()`, `drm_dp_aux_get_crc()`, and `drm_dp_psr_setup_time()`. Quirk support is represented by `struct dpcd_quirk`, `dpcd_quirk_list`, `drm_dp_get_quirks()`, `drm_dp_read_desc()`, and `drm_dp_dump_lttpr_desc()`.

DSC, LTTPR, SDP, PCON, and bandwidth helpers make up the later half of the file: `drm_dp_dsc_sink_bpp_incr()`, `drm_dp_dsc_sink_slice_count_mask()`, `drm_dp_dsc_sink_max_slice_count()`, `drm_dp_dsc_sink_line_buf_depth()`, `drm_dp_dsc_sink_supported_input_bpcs()`, `drm_dp_dsc_sink_max_slice_throughput()`, `drm_dp_dsc_branch_max_overall_throughput()`, `drm_dp_dsc_branch_max_line_width()`, `drm_dp_read_lttpr_common_caps()`, `drm_dp_read_lttpr_phy_caps()`, `drm_dp_lttpr_count()`, `drm_dp_lttpr_max_link_rate()`, `drm_dp_lttpr_init()`, `drm_dp_lttpr_max_lane_count()`, compliance-test pattern helpers, `drm_dp_vsc_sdp_log()`, `drm_dp_as_sdp_log()`, `drm_dp_as_sdp_supported()`, `drm_dp_vsc_sdp_supported()`, `drm_dp_vsc_sdp_pack()`, `drm_dp_get_pcon_max_frl_bw()`, `drm_dp_pcon_*()` FRL/DSC/color-conversion helpers, `drm_edp_backlight_*()`, `drm_panel_dp_aux_backlight()`, `drm_dp_link_symbol_cycles()`, `drm_dp_bw_overhead()`, `drm_dp_bw_channel_coding_efficiency()`, and `drm_dp_max_dprx_data_rate()`.

### Control Flow
For native DPCD reads and writes, callers enter `drm_dp_dpcd_read()` or `drm_dp_dpcd_write()`. Reads may first perform a throwaway probe for non-remote AUX channels to work around monitors that corrupt the first DPCD access after power save. Remote MST AUX channels dispatch to MST DPCD functions; local channels call `drm_dp_dpcd_access()`. That private function locks `aux->hw_mutex`, fails fast if `aux->powered_down`, builds a `drm_dp_aux_msg`, retries up to 32 times, sleeps between non-timeout failures, checks the native AUX reply for ACK/NAK/defer-like error behavior, requires full-size transfers, records the first error, and unlocks before returning.

I2C-over-AUX control starts from the I2C core invoking `drm_dp_i2c_xfer()` through the registered adapter. The helper optionally sends a zero-length address phase, breaks each I2C message into chunks up to `dp_aux_i2c_transfer_size`, drains short replies by adjusting message pointer and size, uses WRITE_STATUS_UPDATE after short/deferred writes, and sends a final zero-length transaction when supported. `drm_dp_i2c_do_msg()` decodes both native and I2C AUX reply fields, handles native defer, I2C defer, NACK, `-EBUSY`, and timeout logging, and adjusts retry count based on estimated I2C bus speed.

Link-training control flow is mostly stateless parsing. Callers read DPCD link status into a six-byte array and ask helpers whether clock recovery, channel equalization, lane symbol lock, or DP 2.x interlane alignment has completed. Delay helpers read or interpret the relevant AUX read-interval registers, differentiating DPRX from LTTPR and 8b/10b from 128b/132b. The functions then return microsecond delays or sleep directly in the older delay APIs.

MST payload control starts by clearing the update-status bit, writing three payload-allocation bytes, then repeatedly reading `DP_PAYLOAD_TABLE_UPDATE_STATUS` with bounded sleeps until `DP_PAYLOAD_TABLE_UPDATED` appears. ACT handling uses `readx_poll_timeout()` until `DP_PAYLOAD_ACT_HANDLED` is set or a read/error timeout occurs.

AUX registration flow is `drm_dp_aux_register()`: warn if `drm_dev` is absent, lazily call `drm_dp_aux_init()` if the I2C adapter is not initialized, set I2C owner/parent/name, register an optional AUX devnode, then add the I2C adapter. Failure after devnode creation unwinds the devnode. `drm_dp_aux_unregister()` unregisters the devnode and removes the I2C adapter. `drm_dp_remote_aux_init()` only sets up CRC work for remote AUX objects.

CRC flow begins with `drm_dp_start_crc()`, which sets `DP_TEST_SINK_START`, stores the CRTC pointer and count, and schedules `crc_work`. The worker waits for vblank while CRTC CRC capture remains open, reads the sink CRC count and six CRC bytes, retries once on `-EAGAIN`, and emits CRC entries. `drm_dp_stop_crc()` clears the test-start bit, flushes the work, and clears `aux->crtc`.

Descriptor and quirk flow reads sink or branch identity blocks, ORs all matching quirk bits from `dpcd_quirk_list` by OUI, device ID, and branch/sink kind, logs the descriptor, and returns the populated `drm_dp_desc`. LTTPR descriptor dumping reads per-repeater OUI registers after validating the requested PHY.

eDP AUX backlight flow begins with `drm_edp_backlight_init()`, which decodes eDP DPCD capability bits, decides whether AUX brightness, AUX enable, LSB brightness registers, or luminance control are available, probes max brightness/PWM settings, and reads current mode and level. `drm_edp_backlight_enable()` restores PWM bit count/frequency where configured, sets DPCD or PWM mode, writes the requested level, and sets the AUX enable bit if supported. `drm_edp_backlight_disable()` clears enable. `drm_panel_dp_aux_backlight()` wires this into a managed Linux backlight device for panel drivers.

PCON FRL/DSC flow is register-oriented: helpers read or write protocol-converter DPCD registers to prepare FRL mode, check FRL readiness, choose bandwidth and training type, enable the HDMI link, read post-FRL mode and trained bandwidth mask, dump lane error counts, determine encoder DSC capabilities, program PPS override buffers or fields, and enable RGB-to-YCbCr conversion bits.

### State And Persistence Behavior
The file keeps no global persistent object state beyond two module parameters and static quirk tables. Most durable state lives in devices and kernel objects passed in by callers:

- `struct drm_dp_aux` holds transfer callbacks, mutexes, the I2C adapter, CEC lock, CRC work, CRTC pointer, CRC count, powered-down state, DPCD probe-disable state, remote-AUX flag, I2C defer/NACK counters, and registration metadata.
- Sink, branch, LTTPR, MST hub, PCON, and eDP panel state persists in DPCD registers accessed through AUX. Examples include `DP_SET_POWER`, link-training status, payload allocation tables, descriptor blocks, DSC/PCON capability and control registers, and eDP backlight registers.
- AUX device nodes and I2C adapters persist in the kernel device model after `drm_dp_aux_register()` until `drm_dp_aux_unregister()`.
- Panel backlight state persists in a managed `backlight_device`, with the private `dp_aux_backlight.enabled` flag mirroring whether the helper believes it enabled the panel.
- Module parameters `dp_aux_i2c_speed_khz` and `dp_aux_i2c_transfer_size` are writable runtime policy knobs and influence all I2C-over-AUX transfers in the module.

Concurrency is guarded primarily by `aux->hw_mutex`, which serializes local AUX hardware access and is also exposed through I2C lock operations. `dpcd_probe_disabled` is accessed with `READ_ONCE()`/`WRITE_ONCE()`. CRC capture uses workqueue state and CRTC CRC-open state. Backlight operations run through the backlight core and issue AUX transactions; drivers must still coordinate panel power sequencing.

### Dependencies
The implementation depends on Linux kernel infrastructure for mutexes, workqueues, sleep/poll helpers, I2C adapters, backlight devices, module parameters, dynamic debug, seq files, and string helpers. DRM dependencies include `drm_dp_helper.h` for DPCD constants and public types, `drm_dp_mst_helper.h` for remote AUX DPCD access, EDID helpers, fixed-point macros, DRM logging, vblank/CRC APIs, connector properties, display modes, HDMI display info, panels, and the optional AUX chardev implementation declared by `drm_dp_helper_internal.h`.

It also depends on driver-supplied `struct drm_dp_aux.transfer()` implementations honoring the AUX contract: only the reply should be mutated in normal cases, return values must match payload bytes transferred, and native/I2C reply bits must reflect sink behavior. Many helpers assume callers pass cached DPCD arrays of the documented size and keep those arrays synchronized with actual sink capabilities.

### Integration Points
GPU drivers use these helpers during connector detection, link training, mode validation, DSC selection, eDP panel enable/disable, MST topology management, and debugfs reporting. MST topology code uses the AUX registration hooks for remote port AUX objects and relies on the same DPCD helpers for payload allocation. Panel drivers can call `drm_panel_dp_aux_backlight()` to create a standard DP AUX backlight device. The DRM display helper module uses the internal AUX devnode init/exit hooks from the companion header. Userspace can indirectly interact with this file through connector properties, I2C/EDID reads, CRC capture, backlight devices, debug output, and optional `/dev/drm_dp_aux*` style char devices.

The exported symbols form a broad ABI inside the kernel module graph; changes affect many DRM drivers outside this specific source directory. The function set also bridges standards domains: base DP DPCD, eDP, MST, LTTPR, DSC, Adaptive Sync SDP, VSC SDP, HDMI PCON FRL, and Linux backlight/I2C frameworks.

### Risks
The highest risk area is AUX retry and locking behavior. Incorrect changes can turn normal sink defers into failures, hide unplug errors, deadlock with I2C locking, spam logs on expected timeouts, or corrupt DPCD reads on affected monitors. Because `drm_dp_dpcd_access()` holds `aux->hw_mutex` around driver callbacks, transfer implementations must not recurse into paths that try to take the same lock.

Link-training helper mistakes can cause unstable links, especially around DP 2.x 128b/132b status bits and LTTPR-specific offsets. Delay calculations intentionally include spec-specific defaults and fallbacks; tightening them without hardware validation risks regressions on real monitors and repeaters.

MST payload helpers manipulate shared hub allocation state. A bad timeout, missing status clear, or incorrect payload triplet can break multi-stream displays or leave hubs with stale payload tables.

The eDP backlight code touches panel brightness and power-control registers. Errors can leave a panel dark, write an unsupported PWM bit count, or mis-scale brightness when min/max bit-count caps are malformed. The luminance path stores millinits in little-endian byte order and divides by 1000 on readback, so unit mistakes are user-visible.

PCON helpers write HDMI FRL and DSC encoder control registers. Invalid bandwidth masks, PPS override programming, or color-conversion bits can break HDMI 2.1 sinks behind DP protocol converters. `drm_dp_pcon_frl_configure_2()` contains an unreachable `ret < 0` check after an immediate `return drm_dp_dpcd_write_byte(...)`, making the local `ret` variable dead and suggesting this helper should be audited if behavior is changed. `drm_dp_pcon_pps_override_buf()` passes `&pps_buf` to a void-buffer write; the address value is effectively the same as the first byte for an array parameter, but the form is easy to misread and should be treated carefully.

Several helpers encode hardware quirks. Removing or broadening entries in `dpcd_quirk_list` can silently affect PSR, sink count, DSC throughput, or link M/N behavior for specific panels and hubs.

Bandwidth math uses fixed-point units, ppm ratios, DP symbol sizes, FEC overhead, MST alignment, and channel-coding efficiency. Unit mistakes may only appear as borderline mode-validation failures at high resolutions or UHBR rates.

### Test Signals
Useful build signals include `allyesconfig`/DRM display-helper builds with and without `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV`, MST, backlight class support, and module builds for `drm_kms_helper`. Static validation should watch for exported-symbol prototype drift against `drm_dp_helper.h`, missing `EXPORT_SYMBOL()` for public helpers, and sparse/smatch warnings in pointer, endian, and array-size handling.

Runtime signals include successful DP/eDP connector detection, stable link training across 8b/10b and UHBR links, correct LTTPR transparent/non-transparent initialization, clean DPCD read/write retries on unplug and sleep/wake, no unexpected AUX timeout log floods, correct EDID reads through I2C-over-AUX, and proper MST payload allocation with ACT completion.

Hardware and integration tests should cover eDP backlight enable/disable and brightness scaling, panel resume from low power, CRC capture start/stop, DSC mode selection on sink and MST branch devices, PCON HDMI FRL bring-up and fallback, VSC/adaptive-sync SDP capability reads, downstream subconnector property updates, and high-bandwidth mode validation with FEC, MST, DSC, SSC, and UHBR flags.

Regression tests should include known quirky devices represented in `dpcd_quirk_list`, a remote MST AUX path, a local SST path, and a powered-down AUX state where DPCD and I2C accesses return `-EBUSY` quickly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper_internal.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper_internal.h

### Purpose
`drm_dp_helper_internal.h` is the private internal header that connects the generic DP helper implementation and MST topology code to the optional DP AUX character-device implementation. It keeps the chardev-specific functions out of the public DRM DP helper header while still allowing `drm_dp_helper.c`, `drm_dp_mst_topology.c`, and the display-helper module init/exit path to call into `drm_dp_aux_dev.c` when `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` is enabled.

### Important APIs, Types, And Functions
The header forward-declares `struct drm_dp_aux` and conditionally exposes four functions:

- `drm_dp_aux_dev_init()` initializes the AUX chardev subsystem.
- `drm_dp_aux_dev_exit()` tears down the AUX chardev subsystem.
- `drm_dp_aux_register_devnode(struct drm_dp_aux *aux)` creates/registers the devnode associated with one AUX channel.
- `drm_dp_aux_unregister_devnode(struct drm_dp_aux *aux)` unregisters the devnode for one AUX channel.

When `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` is disabled, the same names are defined as static inline stubs. The init and register stubs return `0`; the exit and unregister stubs are no-ops. This lets call sites remain unconditional and avoids spreading preprocessor checks across helper and MST code.

### Control Flow
With chardev support enabled, `drm_display_helper_mod.c` calls `drm_dp_aux_dev_init()` and `drm_dp_aux_dev_exit()` during module lifecycle, while `drm_dp_aux_register()` and `drm_dp_aux_unregister()` call the per-AUX devnode helpers as part of AUX adapter registration. MST topology code also registers and unregisters remote port AUX devnodes using the same declarations.

With chardev support disabled, those call sites compile to simple success/no-op paths. `drm_dp_aux_register()` proceeds directly to I2C adapter registration after the stub register call returns `0`; unregister paths can call the stub without checking configuration state.

### State And Persistence Behavior
The header itself owns no state. When chardev support is enabled, the corresponding implementation in `drm_dp_aux_dev.c` owns any class/minor/device-node state and stores per-AUX devnode references reachable through `struct drm_dp_aux`. When disabled, no devnodes are created and no extra persistent state exists.

The compile-time configuration is the main state selector. The stubs intentionally preserve successful control flow so that AUX channels still work for kernel and I2C users even when userspace raw AUX access is unavailable.

### Dependencies
The file depends only on include guards, the `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV` Kconfig symbol, and the existence of `struct drm_dp_aux` as an opaque type. Enabled builds require matching definitions in `drm_dp_aux_dev.c`; disabled builds require no additional source file linkage for these functions.

### Integration Points
This header is included by `drm_dp_helper.c` for local AUX registration and by MST/display-helper code that needs optional raw AUX devnode management. It is part of the internal display helper module boundary, not a public driver API. The public API remains `drm_dp_aux_register()`/`drm_dp_aux_unregister()` plus MST topology helpers; those functions hide whether devnodes exist.

### Risks
The important risk is configuration skew. If enabled prototypes stop matching `drm_dp_aux_dev.c`, chardev builds fail or mis-handle AUX lifetime. If disabled stubs return errors, all AUX registration would fail in configurations without raw AUX userspace support. If callers start depending on devnode side effects while the stubs remain no-ops, behavior will differ between Kconfig variants.

Because devnodes expose raw AUX access to userspace, lifetime ordering matters in enabled builds: unregister must run before the AUX backing object is destroyed, and registration failures must be unwound. The header's unconditional API shape makes that easier, but it also means call sites must continue to call the unregister helper on every registered AUX object.

### Test Signals
Build-test both `CONFIG_DRM_DISPLAY_DP_AUX_CHARDEV=y/m` and disabled configurations. In enabled builds, module init should create the AUX chardev infrastructure, AUX registration should create devnodes for local and MST remote AUX channels, and unregister should remove them without use-after-free warnings. In disabled builds, DP connector detection, AUX DPCD reads, I2C-over-AUX EDID reads, and MST operation should still work, with no unresolved references to `drm_dp_aux_dev_*` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_helper_internal.h -->
