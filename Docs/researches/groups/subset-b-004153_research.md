# Research: subset-b-004153

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.h

This header defines the firmware-to-host HFI message ABI used by the Qualcomm Venus driver. It is not executable logic; its purpose is to give `hfi_msgs.c` and the Venus transport a typed view of system messages, session completions, event notifications, fill-buffer-done packets, debug strings, and coverage records returned through the HFI message queue.

Important API elements are the `HFI_MSG_*` packet type constants, picture/frame flag constants, and packet structs such as `hfi_msg_sys_init_done_pkt`, `hfi_msg_event_notify_pkt`, `hfi_msg_session_empty_buffer_done_pkt`, `hfi_msg_session_fbd_compressed_pkt`, and `hfi_msg_session_fbd_uncompressed_plane0_pkt`. The header also declares `hfi_process_watchdog_timeout()` and `hfi_process_msg_packet()`, which are the integration points consumed by `hfi_venus.c` after reading messages from firmware.

Control flow is indirect: `venus_isr_thread()` drains the message queue, passes each packet header to `hfi_process_msg_packet()`, and branches on the returned message code for system init/resource/power-collapse handling. The flexible array members in many structs model variable-sized property payloads and multi-plane buffer metadata, so packet size validation in the queue reader is critical.

State and persistence are limited to wire data. Firmware state is reflected through packet fields such as `error_type`, `event_id`, `filled_len`, timestamps, picture type, output tags, and buffer addresses. The structs depend on lower-level packet headers from `hfi_helper.h`/`hfi.h` and Linux fixed-width types.

Risks center on ABI drift and bounds. Any field layout change can corrupt message parsing, buffer completion, or event handling. Flexible arrays require callers to validate packet size before dereferencing. Test signals include successful firmware init, session start/stop acknowledgements, fill-buffer-done delivery for compressed and raw paths, EOS/source-change events, and watchdog/system-error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.c

This file parses HFI capability/property payloads into `venus_core` platform capability state. It supports two modes: for v4/v6 it prefers static platform capability tables from `hfi_platform_get()`, while older or instance-specific paths parse firmware-provided property records.

Key functions include `hfi_parser()`, `hfi_platform_parser()`, `init_codecs()`, `parse_codecs()`, `parse_codecs_mask()`, `parse_raw_formats()`, `parse_caps()`, `parse_profile_level()`, and `parse_alloc_mode()`. The `for_each_codec()` helper applies parsed data to matching `hfi_plat_caps` entries, while `parser_init()` and `parser_fini()` handle the Venus v1xx per-instance validity behavior.

The main control flow starts by trying static platform parsing for core-level calls. If that path succeeds, it fills `core->enc_codecs`, `core->dec_codecs`, `core->codecs_count`, `core->max_sessions_supported`, and `core->caps` from platform data. Otherwise `hfi_parser()` validates 32-bit alignment and walks a property stream by reading a property id word and advancing by the parser-reported payload size. Codec-supported records seed capability entries, mask records select the target codec/domain, then format/capability/profile/allocation records append arrays onto matching capability entries.

State is held in `venus_core`: codec bitmasks, max sessions, capability arrays, raw format arrays, profile-level arrays, and dynamic-buffer-mode flags. Dependencies include `core.h`, `hfi_helper.h`, and `hfi_platform`. Integration points include V4L2 format enumeration, decoder format clamping, control limits, and buffer-mode setup through helpers that query `venus_caps_by_codec()`.

Risks include trusting payload-internal counts and size math. The code checks max entry counts but advances by parser return values that must match firmware layout; malformed `format_entries` or plane counts can desynchronize parsing. Static table fallback means v4/v6 capability regressions may not be visible through firmware parser tests. Test signals are correct codec enumeration, min/max frame constraints, raw format availability, profile/level exposure, dynamic buffer mode behavior, and error returns for truncated or unaligned property payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.h

This header exposes the HFI parser and inline capability lookup helpers. It is the small public interface used by decoder, encoder, and PM paths to query per-instance firmware/platform capability bounds.

The exported function is `hfi_parser(struct venus_core *core, struct venus_inst *inst, void *buf, u32 size)`. Inline APIs include `get_cap()`, `cap_min()`, `cap_max()`, `cap_step()`, and domain-specific helpers such as `frame_width_min()`, `frame_width_max()`, `frame_height_step()`, `frate_max()`, `core_num_max()`, and `mbs_per_frame_max()`.

Control flow in the inlines is simple: `get_cap()` resolves the `hfi_plat_caps` entry for the instance codec/session via `venus_caps_by_codec()`, scans its capability array for the requested HFI capability type, and returns the requested min/max/step field. Callers use these helpers during format clamping, frame-size enumeration, PM core routing, and buffer size estimation.

The header does not own persistent state; it reads `inst->core`, `inst->hfi_codec`, `inst->session_type`, and `core->caps`. Dependencies include `core.h` and the HFI capability constants. Integration points are broad because these helpers are the main bridge from parsed capabilities to V4L2 user-visible constraints.

Risks are silent zero fallback and stale capability state. If parsing failed or the codec/domain is not found, helpers return zero, which can cause invalid clamp ranges or route decisions if callers do not validate session initialization. Test signals include sane `VIDIOC_ENUM_FRAMESIZES`, format try/set clamping, and PM routing with max video core capability on multi-core platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs.h

This header defines the input contract for platform-calculated HFI buffer requirements. It is primarily used by v6 platform support, where the driver computes buffer sizes instead of relying entirely on firmware.

The central type is `struct hfi_plat_buffers_params`. It carries coded and output dimensions, codec, HFI color formats for OPB/DPB, HFI version, VPP pipe count, and a decoder/encoder union. Decoder parameters include max macroblocks, buffer-size limit, secondary-output mode, and interlace state. Encoder parameters include work mode, rate-control type, B-frame count, and ten-bit mode. The exported function is `hfi_plat_bufreq_v6()`.

Control flow is external: helpers populate this struct from a `venus_inst`, then call the platform `bufreq` callback. `hfi_plat_bufreq_v6()` fills a mutable `hfi_buffer_requirements` for input, output, output2, scratch, scratch1, scratch2, and persistent buffers based on session type and buffer type.

There is no persistent state in this header; it defines a transient calculation request. Dependencies are `linux/types.h`, `hfi_helper.h`, and the HFI version/buffer requirement ABI.

Risks involve incomplete or inconsistent parameter population. Wrong DPB/OPB format, pipe count, bit depth, or max-macroblock limits can under-allocate firmware buffers. Test signals include successful v6 decoder and encoder stream-on at multiple resolutions, 10-bit UBWC operation, interlaced decode, multi-pipe routing, and correct minimum buffer counts reported to V4L2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs_v6.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs_v6.c

This file implements Iris/v6 platform buffer-requirement calculations for decode and encode sessions. It encodes firmware-aligned formulas for input bitstream buffers, raw output buffers, internal scratch buffers, scratch1/scratch2 working buffers, and persistent codec-private buffers.

Important APIs are the exported `hfi_plat_bufreq_v6()` and the internal `bufreq_dec()`/`bufreq_enc()` dispatchers. Decoder sizing is organized through `struct dec_bufsize_ops` tables for H.264, HEVC, VP8, VP9, and MPEG2. Encoder sizing uses `struct enc_bufsize_ops` for H.264, HEVC, and VP8. Notable calculators include `calculate_dec_input_frame_size()`, `calculate_enc_output_frame_size()`, `calculate_enc_scratch_size()`, `calculate_enc_scratch1_size()`, `enc_scratch2_size()`, codec-specific `*_scratch_size()`, `*_scratch1_size()`, and `*_persist1_size()`.

Control flow starts in `hfi_plat_bufreq_v6()`, branches by session type, selects codec operations, initializes common requirement fields, then switches on HFI buffer type. Input buffers use minimum counts and compressed/raw frame size formulas. Output buffers use raw frame size helpers and codec-specific min counts. Internal buffers combine line-buffer, command-buffer, collocated-motion-vector, UBWC metadata, VPP pipe, reference count, ten-bit, interlace, split-output, work-mode, and rate-control terms.

State is transient: the file mutates the caller-provided `hfi_buffer_requirements` and reads only `hfi_plat_buffers_params`. Dependencies include Linux alignment helpers, V4L2 pixel formats, `hfi.h`, `hfi_helper.h`, and `venus_helper_get_framesz_raw()`.

Risks are high because constants mirror firmware expectations. Arithmetic overflow, width/height alignment mistakes, wrong minimum counts, VP9/HEVC 10-bit assumptions, or incorrect secondary-output handling can produce under-sized DMA buffers and firmware failures. Test signals include `REQBUFS` minimum counts, successful stream-on for each codec, 4K/8K boundary cases, 10-bit UBWC/P010, VP9 minimum buffer quirk, rate-control-off encoder output sizing, and internal buffer allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_plat_bufs_v6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.c

This file is the platform dispatch layer for HFI version-specific capability, codec, frequency, and buffer-requirement callbacks. It maps an `enum hfi_version` to the v4 or v6 platform tables and provides small wrappers used by parser and PM code.

Key functions are `hfi_platform_get()`, `hfi_platform_get_codec_vpp_freq()`, `hfi_platform_get_codec_vsp_freq()`, `hfi_platform_get_codec_lp_freq()`, and `hfi_platform_get_codecs()`. The dispatch target is `struct hfi_platform` from `hfi_platform.h`, with concrete instances in `hfi_platform_v4.c` and `hfi_platform_v6.c`.

Control flow is simple: version lookup returns `hfi_plat_v4`, `hfi_plat_v6`, or `NULL`; wrapper functions guard missing platforms/callbacks and return zero or `-EINVAL` on unsupported versions. `hfi_platform_get_codecs()` additionally masks VP8 on IRIS2_1 cores.

The file stores no state. It reads `core->res->hfi_version` and hardware predicates from `core.h`. Integration points include `hfi_parser.c` static capability loading and `pm_helpers.c` frequency estimation through helper wrappers.

Risks include callback mismatch and silent zero frequencies. `hfi_platform_get_codec_vsp_freq()` checks `codec_vpp_freq` before calling `codec_vsp_freq`, so a platform with only VSP callback would be skipped. Unsupported HFI versions fall back to firmware parser paths where available, but PM frequency lookup may degrade to zero. Test signals include codec enumeration on v4/v6, IRIS2_1 VP8 filtering, and nonzero VPP/VSP/low-power frequencies for supported pixel formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.h

This header defines the platform capability model used by the Venus HFI driver. It provides fixed-size arrays and callback contracts for codec support, format support, capability ranges, profile levels, performance frequencies, and platform-specific buffer requirements.

Important types are `struct raw_formats`, `struct hfi_plat_caps`, `struct hfi_platform_codec_freq_data`, and `struct hfi_platform`. Constants such as `MAX_PLANES`, `MAX_FMT_ENTRIES`, `MAX_CAP_ENTRIES`, `MAX_ALLOC_MODE_ENTRIES`, `MAX_CODEC_NUM`, and `MAX_SESSIONS` bound parser and table storage. Externs declare `hfi_plat_v4` and `hfi_plat_v6`; functions expose platform lookup, frequency lookup, and codec enumeration.

Control flow is callback-driven. `hfi_parser.c` asks the platform for static capabilities; PM code asks for codec frequencies; v6 platform uses the `bufreq` callback to compute requirements. `hfi_plat_caps.valid` is specifically documented as Venus v1xx parser state, while static v4/v6 tables are copied wholesale into `core->caps`.

State ownership is external: the header describes data copied into `venus_core` and read by `venus_inst` helpers. Dependencies include V4L2 pixel formats, `hfi.h`, `hfi_helper.h`, and `hfi_plat_bufs.h`.

Risks include fixed-array truncation and semantic mismatch between V4L2 pixel formats and HFI codec masks. Adding codecs or formats requires updating max constants, parser bounds, and platform tables together. Test signals are complete enum-format output, profile/level controls, frame-size limits, PM frequency scaling, and v6 buffer requirements for all advertised codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v4.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v4.c

This file defines static Venus HFI v4 platform capabilities and frequency hints. It covers full and lite variants, advertising decode/encode codecs, frame limits, bitrates, profile levels, raw formats, dynamic buffer mode support, and per-codec frequency data.

Important data are the `caps[]` and `caps_lite[]` tables, `codec_freq_data[]`, and `codec_freq_data_lite[]`. Key functions are `get_capabilities()`, `get_codecs()`, `get_codec_freq_data()`, `codec_vpp_freq()`, `codec_vsp_freq()`, and `codec_lp_freq()`. The exported object is `hfi_plat_v4`.

Control flow is table selection by `is_lite(core)`. `get_capabilities()` returns either lite or full tables with entry count. `get_codecs()` walks selected capabilities and builds encoder/decoder bitmasks. Frequency lookup matches V4L2 pixel format and session type to VPP, VSP, and low-power frequency values. `hfi_plat_v4` does not provide a `bufreq` callback, so buffer sizing follows other firmware/helper paths.

The file owns immutable static data only. Its contents become persistent runtime state when copied into `core->caps` by `hfi_platform_parser()`. Dependencies include `core.h`, HFI constants, and V4L2 pixel format constants.

Risks include table incompleteness, lite/full mismatches, and frequency underestimation. If a codec appears in format lists but not frequency data, PM scaling can receive zero. Capability limits directly affect user-visible `TRY_FMT`, `ENUM_FRAMESIZES`, and controls. Test signals include full/lite codec enumeration, HEVC/VP9 10-bit format availability, max-resolution clamping, profile-level controls, and decode/encode throughput without clock under-voting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v6.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v6.c

This file defines static HFI v6 platform capabilities and frequency hints, and attaches the v6 buffer-requirement calculator. It advertises higher decode limits for H.264/HEVC/VP9, encoder support for H.264/HEVC/VP8, UBWC/10-bit formats where supported, and frequency rows used by PM scaling.

Key data are the `caps[]` table and `codec_freq_data[]`. Key functions mirror v4: `get_capabilities()`, `get_codecs()`, `get_codec_freq_data()`, `codec_vpp_freq()`, `codec_vsp_freq()`, and `codec_lp_freq()`. The exported `hfi_plat_v6` includes `.bufreq = hfi_plat_bufreq_v6`, making this platform responsible for calculated buffer requirements.

Control flow rejects lite cores by returning no capabilities/codecs/frequencies for `is_lite(core)`. For non-lite v6, `get_codecs()` returns fixed encoder and decoder bitmasks and count, while capability parsing copies eight entries into `core->caps`. Frequency lookup is keyed by V4L2 pixel format and session type.

State is immutable static table data copied into `venus_core`; buffer sizing state is delegated to `hfi_plat_bufs_v6.c`. Dependencies include `core.h`, `hfi_platform.h`, V4L2 formats, HFI codec/capability constants, and the v6 buffer calculator.

Risks include the hard-coded codec count, no lite fallback, and tight coupling with calculated buffer sizes. Advertising 8K decode or 10-bit formats without matching buffer formulas and PM votes can cause firmware stream failures. Test signals include v6 codec enumeration, 8K frame-size constraints, v6 `REQBUFS` sizes, PM frequency votes for VP8/VP9 VSP paths, and rejection/alternate handling of lite cores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_platform_v6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.c

This file implements the Venus HFI transport and the `hfi_ops` backend. It allocates firmware shared queues, boots the video firmware, writes HFI command packets, drains message/debug queues from interrupts, handles power-collapse handshakes, and exposes session operations used by decoder/encoder helpers.

Important types are internal `hfi_queue_table_header`, `hfi_queue_header`, `mem_desc`, `iface_queue`, `enum venus_state`, and `struct venus_hfi_device`. Key functions include queue primitives `venus_write_queue()`/`venus_read_queue()`, boot and power paths `venus_run()`, `venus_boot_core()`, `venus_power_on()`, `venus_power_off()`, AXI halt logic, queue setup/reinit, `venus_core_init()`, session commands (`venus_session_init/end/abort/flush/start/stop/etb/ftb/set_buffers/unset_buffers`), interrupt handlers `venus_isr()`/`venus_isr_thread()`, suspend/resume implementations, and exported lifecycle functions `venus_hfi_create()`, `venus_hfi_destroy()`, and `venus_hfi_queues_reinit()`.

Control flow starts at `venus_hfi_create()`, which allocates `venus_hfi_device`, initializes DMA shared queues/SFR, and installs `venus_hfi_ops` into `core->ops`. Runtime resume powers hardware, writes queue/SFR addresses to registers, boots firmware, then `venus_core_init()` sends system init, image version, debug, power-control, idle, and UBWC properties. Session calls construct HFI packets through `hfi_cmds` helpers and write them to the command queue. Interrupt top half records/clears status and wakes the thread; the thread drains message packets, hands them to `hfi_process_msg_packet()`, completes resource or power-collapse completions, handles sys-error events, and flushes debug logs.

State includes `power_enabled`, `suspended`, HFI init/deinit state, last packet type, IRQ status, completions, DMA queue memory, SFR memory, and per-queue read/write indexes shared with firmware. Dependencies include register offsets from `hfi_venus_io.h`, packet builders, message processors, firmware resources, DMA APIs, completions, mutexes, and hardware-generation predicates.

Risks are concurrency, ordering, and firmware ABI sensitivity. Queue read/write relies on memory barriers and index validation; bad packet sizes are dropped or rejected. Suspend paths differ by generation and require PC_READY/WFI/idle checks. System error sets state to deinit and SFR logging is rate-limited. Test signals include firmware boot, SYS_INIT_DONE, session init/end, ETB/FTB traffic, debug queue output, watchdog/system-error recovery, runtime suspend/resume, SSR trigger, and queue reinitialization after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.h

This header is the public lifecycle interface for the Venus HFI transport backend. It intentionally hides the queue, register, and power-management internals defined in `hfi_venus.c`.

The exported APIs are `venus_hfi_create(struct venus_core *core)`, `venus_hfi_destroy(struct venus_core *core)`, and `venus_hfi_queues_reinit(struct venus_core *core)`. `venus_hfi_create()` allocates transport state and installs HFI ops on the core, `venus_hfi_destroy()` tears it down, and `venus_hfi_queues_reinit()` resets shared queue headers after hardware reset or recovery.

Control flow is driven by the core probe/remove and recovery paths outside this header. Callers only need a `venus_core`; the private `venus_hfi_device` remains opaque through `core->priv`.

The header stores no state. Its dependency is the forward declaration of `struct venus_core`; implementation dependencies are kept private to reduce coupling.

Risks are lifecycle ordering. Destroy must only run after users are quiesced, and queue reinitialization assumes DMA queue memory is still allocated. Test signals include successful core probe, clean module/remove path, recovery/reset path that reinitializes queues, and absence of use-after-free around `core->ops` and `core->priv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus_io.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus_io.h

This header defines Venus hardware register offsets, bit masks, base offsets, and timeouts used by the HFI transport and PM helpers. It is the register ABI for CPU control/status, interrupt controller, wrapper, VBIF, vcodec power, TrustZone wrapper, and always-on wrapper blocks.

Important groups include VBIF halt registers, CPU CS queue/control registers (`VIDC_CTRL_INIT`, `CPU_CS_SCIACMDARG*`, `SFR_ADDR`, `UC_REGION_*`), soft interrupt registers, wrapper interrupt status/mask/clear registers, CPU halt/status/reset registers, memory protection range registers, v4 vcodec power registers, v6 core power registers, TrustZone CPU status/reset registers, and AON MVP NOC LPI registers.

Control flow is external. `hfi_venus.c` uses these constants to boot firmware, signal host-to-controller interrupts, clear firmware interrupts, halt AXI for powerdown, poll idle/PC-ready status, and read hardware version. `pm_helpers.c` uses vcodec power-control/status offsets for v3/v4 core power sequencing.

The header has no persistent state. Dependencies are Linux bit macros and exact SoC register maps. Integration points are all low-level hardware access paths in Venus HFI and PM code.

Risks are severe because wrong offsets or masks can hang hardware or break suspend/resume. Generation-specific constants are easy to misuse: v6 and v4-lite soft interrupt and watchdog bits differ from older cores. Test signals include successful boot register programming, interrupt delivery/clearing, AXI halt polling, vcodec power-domain transitions, runtime suspend/resume, and hardware-version logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.c

This file implements generation-specific power, clock, bandwidth, OPP, reset, power-domain, and core-routing operations for Venus. It returns a `venus_pm_ops` table for HFI v1, v3, v4, and v6 platforms.

Important functions include core clock helpers, vcodec clock helpers, `load_per_instance()`, `load_scale_bw()`, `load_scale_v1()`, v3 `vcodec_control_v3()`, v4/v6 `vcodec_control_v4()`, `poweron_coreid()`, `poweroff_coreid()`, `decide_core()`, `acquire_core()`, `release_core()`, `coreid_power_v4()`, `vcodec_domains_get()`, reset helpers, `core_get_v4()`, `core_power_v4()`, `calculate_inst_freq()`, `load_scale_v4()`, and exported `venus_pm_get()`.

Control flow begins during core/decoder/encoder probe through `core_get`, `vdec_get`, and `venc_get`. Runtime PM calls `core_power` or vcodec power callbacks to enable clocks, resets, OPP domains, and codec subdomains. Stream start calls `venus_pm_acquire_core()` via the inline wrapper, which may decide a target core based on current instance load and set `HFI_PROPERTY_CONFIG_VIDEOCORES_USAGE`. Load scaling calculates macroblocks-per-second and bitstream bandwidth, votes interconnect bandwidth, and sets OPP/clock rates. Stream teardown releases core usage counts and powers off unused codec cores.

State lives in `venus_core` and `venus_inst`: clock handles, PM domain lists, reset controls, usage counts, selected `clk_data.core_id`, per-instance frequency data, `VENUS_LOW_POWER` flags, and global `legacy_binding`. Dependencies include clk, interconnect, OPP, PM runtime/domain, reset, V4L2 mem2mem, HFI parser capability helpers, platform frequency helpers, and register offsets.

Risks include global `legacy_binding` affecting multiple cores, unbalanced PM runtime on errors, wrong core routing under concurrent sessions, clock under-voting for high bitrate decode, and low-power mode changes that depend on HFI property success. Test signals include probe on legacy and non-legacy bindings, dual-core session placement, runtime suspend/resume, OPP vote changes under load, bandwidth votes for 8-bit/10-bit streams, and clean release after session errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.h

This header defines the Venus PM operation table and small inline helpers used by decoder/encoder code. It abstracts generation-specific power and load-scaling behavior behind `struct venus_pm_ops`.

Important API elements are `POWER_ON`, `POWER_OFF`, `struct venus_pm_ops`, `venus_pm_get()`, `venus_pm_load_scale()`, `venus_pm_acquire_core()`, and `venus_pm_release_core()`. The ops table separates core power from vdec/venc subdevice power, optional per-core power routing, and per-instance load scaling.

Control flow is callback-based. Core probe selects ops by HFI version; decoder and encoder runtime PM call vdec/venc callbacks; stream start/stop use the inline acquire/release helpers; buffer processing and configuration call load scaling when dimensions, payloads, or session state change.

The header owns no state. It reads `inst->core`, `core->pm_ops`, and optional callback pointers. Dependencies are forward declarations for `struct device`, `struct venus_core`, and `struct venus_inst` from included compile context.

Risks are silent no-op behavior if callbacks are absent. That is intentional for unsupported generations but can hide missing PM setup. Test signals include non-null selected ops for each supported HFI version, successful stream start with `coreid_power`, load scaling returning zero where unsupported, and balanced release on close/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/pm_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.c

This file implements the Qualcomm Venus V4L2 mem2mem decoder device. It exposes compressed OUTPUT queues, raw CAPTURE queues, format negotiation, buffer queue setup, stream state transitions, firmware session setup, dynamic resolution change handling, buffer completion, runtime PM integration, and platform driver registration.

Important APIs and callbacks include V4L2 ioctl handlers (`vdec_querycap`, `vdec_enum_fmt`, `vdec_try_fmt`, `vdec_s_fmt`, `vdec_g_fmt`, `vdec_g_selection`, `vdec_s_parm`, `vdec_decoder_cmd`), VB2 ops (`vdec_queue_setup`, `vdec_start_streaming`, `vdec_stop_streaming`, `vdec_vb2_buf_queue`, cleanup), HFI instance ops (`vdec_buf_done`, `vdec_event_notify`, `vdec_flush_done`), lifecycle functions (`vdec_open`, `vdec_close`, `vdec_probe`, `vdec_remove`), and runtime PM callbacks.

Control flow starts at probe, which registers a `video_device` and enables autosuspend. Open allocates `venus_inst`, initializes lists, controls, m2m queues, default formats, HFI session, and V4L2 fh. Format setting clamps dimensions using parsed capabilities and stores raw/compressed sizes. Queue setup starts a firmware session if needed, queries buffer requirements, and returns minimum counts. OUTPUT stream-on powers the decoder, acquires a core, configures properties/work route/output, verifies buffer counts, starts VB2/HFI streaming, and queues initial compressed buffers. CAPTURE stream-on configures/reconfigures output buffers and queues DPB/capture buffers. Firmware events move `codec_state` through DEINIT, INIT, CAPTURE_SETUP, DECODING, DRAIN, STOPPED, DRC, and SEEK. Close tears down sessions after buffers are released.

State is per-instance: formats, dimensions, crop, colorspace, buffer sizes/counts, sequence counters, codec state, streamon flags, bit depth, DPB/internal/registered buffer lists, PM/core acquisition state, drain/reconfig flags, and timestamps/metadata. Dependencies include V4L2/VB2/mem2mem, HFI helpers, parser capabilities, PM helpers, DMA-contig memory, and firmware event callbacks.

Risks are state-machine edge cases: dynamic resolution change, EOS drain, streamoff ordering, firmware quirks for NULL EOS on old IRIS2 firmware, VP9 min-buffer override, and session release after partial failures. Test signals include format enumeration, `TRY_FMT`/`S_FMT`, `REQBUFS` min counts, stream-on/off both queues, EOS command, dynamic resolution change with source-change event, 10-bit format switch, session error recovery, runtime autosuspend, and close with active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.h

This header provides the minimal public decoder interface for other Venus files. It forward declares `struct venus_inst` and exports decoder control initialization.

The only API is `int vdec_ctrl_init(struct venus_inst *inst)`, implemented in `vdec_ctrls.c` and called from `vdec_open()` before the instance is exposed through V4L2 file-handle setup.

Control flow is simple: decoder instance allocation calls `vdec_ctrl_init()`, which initializes the V4L2 control handler and stores decoder-specific defaults in `inst->controls.dec` as users set controls.

The header has no state. It depends only on a forward declaration, keeping V4L2 control details private to the implementation.

Risks are limited to lifecycle ordering: callers must free the control handler on later open failures and during close/common cleanup. Test signals include successful decoder open, visible decoder controls through V4L2 query APIs, and clean error unwind if control initialization fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec_ctrls.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec_ctrls.c

This file initializes and services V4L2 controls for Venus decoder instances. It maps standard MPEG/decoder controls to `inst->controls.dec` and exposes volatile firmware-derived profile, level, and minimum capture-buffer data.

Important functions are `vdec_ctrl_init()`, `vdec_op_s_ctrl()`, and `vdec_op_g_volatile_ctrl()`. Controls include MPEG4/H264/VP8/VP9 profile and level menus, MPEG4 deblock filter, `V4L2_CID_MIN_BUFFERS_FOR_CAPTURE`, display delay and enable controls, and conceal color.

Control flow starts in `vdec_ctrl_init()`, which creates a control handler with menu/std controls and marks profile/level/min-buffer controls volatile where firmware or current stream data can update them. `vdec_op_s_ctrl()` copies user values into decoder control state. `vdec_op_g_volatile_ctrl()` refreshes profile/level through `venus_helper_get_profile_level()` and minimum capture buffers through `venus_helper_get_bufreq(HFI_BUFFER_OUTPUT)`.

State persists in `inst->ctrl_handler` and `inst->controls.dec`: profile, level, post-loop deblock mode, display delay, display-delay enable, and conceal color. Dependencies include V4L2 controls, core/helper utilities, HFI buffer requirements, and HFI version-specific count accessors.

Risks include exposing unsupported profile/level combinations through static masks, stale volatile values before firmware has parsed stream headers, and buffer-minimum queries failing during session transitions. Test signals include V4L2 control enumeration, set/get for each control, volatile profile/level after sequence parsing, minimum capture buffers matching firmware/platform requirements, and proper handler cleanup on init error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/vdec_ctrls.c -->
