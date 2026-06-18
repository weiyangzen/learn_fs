# Research: subset-b-004150

Grouped research for Qualcomm Iris media driver files under `sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris`. Each section preserves its source path and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.c

## Purpose
`iris_buffer.c` owns Iris buffer sizing, internal DMA buffer lifecycle, firmware queue/release transitions, deferred queue handling, and conversion of firmware-completed buffers back to V4L2 mem2mem/vb2 completion. It is central to both decoder and encoder paths because all HFI generations use `iris_queue_buffer()` and `iris_vb2_buffer_done()` as the common buffer bridge.

## Important APIs, Types, And Functions
The public entry points are `iris_get_buffer_size()`, `iris_get_internal_buffers()`, `iris_create_internal_buffers()`, `iris_queue_internal_buffers()`, `iris_queue_internal_deferred_buffers()`, `iris_destroy_*_internal_buffers()`, `iris_alloc_and_queue_persist_bufs()`, `iris_alloc_and_queue_input_int_bufs()`, `iris_queue_buffer()`, `iris_queue_deferred_buffers()`, `iris_vb2_buffer_done()`, and `iris_vb2_queue_error()`. Private size helpers compute NV12, QC08C/UBWC, decoder bitstream, and encoder bitstream sizes. Internal buffer helpers allocate `struct iris_buffer` objects using `dma_alloc_attrs()` with write-combine/no-kernel-mapping attributes and track them under `inst->buffers[type].list`.

## Control Flow
Format-dependent size helpers pick `inst->fmt_dst` for decoder output or `inst->fmt_src` for encoder input, then apply hardware-required alignment. `iris_get_buffer_size()` dispatches by domain and `enum iris_buffer_type`; decoder DPB always uses QC08C sizing. Internal buffer discovery uses platform tables split by decoder/encoder and input/output plane, fills `min_count` and size from VPU helpers, then creation allocates each DMA buffer and queues it through `core->hfi_ops->session_queue_buf`. DPB buffers are deferred until `IRIS_INST_STREAMING`; deferred user buffers are queued later after power scaling.

## State And Persistence Behavior
Buffer state is held in `struct iris_buffer.attr` bits: `DEFERRED`, `QUEUED`, `PENDING_RELEASE`, `DEQUEUED`, and `BUFFER_DONE`. Internal DMA allocations persist on the instance lists until release or stream teardown; forced teardown also destroys persist or ARP buffers depending on domain. `iris_vb2_buffer_done()` removes the vb2 buffer from the mem2mem queue, sets payload/timestamp/sequence, propagates timestamp metadata, emits EOS events on `V4L2_BUF_FLAG_LAST`, and marks the mem2mem context stopped.

## Dependencies And Integration Points
This file depends on V4L2 mem2mem/vb2 APIs, DMA mapping, `iris_hfi_command_ops`, platform buffer tables, `iris_vpu_buffer` sizing/count helpers, `iris_power` scaling, and instance state from `iris_instance.h`. It is called by streamon/streamoff code, HFI response handlers, qbuf paths, and platform-specific VPU buffer sizing. EOS propagation integrates with `v4l2_event_queue_fh()` and `v4l2_m2m_mark_stopped()`.

## Risks And Test Signals
Risk concentrates in alignment math, buffer attr transitions, and list removal. `iris_vb2_buffer_to_driver()` in another file computes `bytesused - data_offset`; callers should ensure vb2 validation prevents underflow before queueing. `iris_destroy_internal_buffers(..., force=false)` intentionally leaves queued buffers alive, so tests should cover firmware returning release responses after streamoff. Useful signals are v4l2-compliance queue tests, decoder DRC/drain EOS tests, encoder EOS tests, DPB split-mode buffer return tests, and fault injection for queue failures and DMA allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.h

## Purpose
`iris_buffer.h` defines the driver-facing buffer model shared by vb2, Iris instance state, HFI command builders, and HFI response handlers. It is the contract that lets generation-specific firmware code and generic V4L2 code agree on buffer type, address, payload, timestamp, and lifecycle state.

## Important APIs, Types, And Functions
The key type is `enum iris_buffer_type`, with user-visible `BUF_INPUT`/`BUF_OUTPUT` plus internal buffers such as `BUF_BIN`, `BUF_ARP`, `BUF_COMV`, `BUF_NON_COMV`, `BUF_LINE`, `BUF_DPB`, `BUF_PERSIST`, `BUF_SCRATCH_1`, `BUF_SCRATCH_2`, `BUF_VPSS`, and `BUF_PARTIAL`. `enum iris_buffer_attributes` declares lifecycle bits used across queue, response, release, and vb2 completion paths. `struct iris_buffer` embeds `struct vb2_v4l2_buffer`, carries DMA address information, data offsets, V4L2 flags, timestamps, and attr bits. `struct iris_buffers` is the per-type instance list, minimum count, and buffer size.

## Control Flow
The header exports creation, queueing, release, destroy, deferred queue, and vb2 completion helpers implemented by `iris_buffer.c`. HFI Gen1 and Gen2 command files consume `enum iris_buffer_type` to translate driver buffers to firmware buffer identifiers. HFI response files mutate `attr` and call `iris_vb2_buffer_done()` after firmware returns input or output buffers.

## State And Persistence Behavior
Persistent state is per-instance: `inst->buffers[BUF_TYPE_MAX]` stores list heads, min counts, and sizes, while each `struct iris_buffer` records its current firmware/vb2 lifecycle through attr bits. Internal buffers are heap objects with DMA backing; user buffers are vb2-backed and are not allocated here.

## Dependencies And Integration Points
The file depends on `videobuf2-v4l2.h` and forward-declares `struct iris_inst`. It is included broadly by instance, HFI common, HFI command/response, VPU buffer, and common streaming code. `to_iris_buffer()` is the standard conversion from embedded vb2 buffer to Iris metadata.

## Risks And Test Signals
Because buffer attrs are bit flags rather than a strict enum, illegal combinations can occur if command and response paths diverge. Tests should assert that input and output buffers are completed once, queued buffers are never freed before firmware release, and each internal buffer type is translated by both Gen1 and Gen2 command/response code where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.c

## Purpose
`iris_common.c` contains streaming and vb2 helper logic that is shared by decoder and encoder implementations. It converts vb2 buffers into Iris buffers, preserves timestamp metadata, coordinates input/output streamon across HFI sessions, and performs streamoff cleanup/error fallback.

## Important APIs, Types, And Functions
`iris_vb2_buffer_to_driver()` copies vb2 plane fd, length, offset, bytesused, flags, timestamp, index, and mapped Iris buffer type into `struct iris_buffer`. `iris_set_ts_metadata()` stores timecode and timestamp-source flags in `inst->tss[]` for later capture-buffer restoration. `iris_process_streamon_input()` and `iris_process_streamon_output()` wrap HFI session starts, power scaling, DRC/drain/first-IPSC pause/resume behavior, and instance state transitions. `iris_session_streamoff()` stops a plane and flushes deferred buffers, killing the session on stop/state failure.

## Control Flow
Input streamon scales power, sends `session_start()` on the output queue, clears input pause, may pause decoder input again when DRC/drain/first-IPSC state requires output reconfiguration, then changes instance state to input-streaming or streaming. Output streamon handles DRC/drain flags, reallocates and queues input internal buffers for first-IPSC or DRC, reapplies stage/pipe properties, resumes input if it had been paused, starts capture, and clears completed sub-states. Streamoff maps the V4L2 plane to `BUF_INPUT` or `BUF_OUTPUT`, sends HFI `session_stop()`, updates instance state, and completes deferred vb2 buffers with zero payload.

## State And Persistence Behavior
The file mutates `inst->state`, `inst->sub_state`, `inst->last_buffer_dequeued`, timestamp metadata ring state, and deferred buffer attr bits. It uses completions indirectly through HFI ops and state helpers. On HFI failure during streamoff it calls `session_close()` and sets instance error state, but still returns deferred buffers to avoid userspace hangs.

## Dependencies And Integration Points
It depends on V4L2 mem2mem, `iris_ctrls` for `iris_set_stage()` and `iris_set_pipe()`, `iris_power`, `iris_buffer`, HFI command ops, and instance state helpers. Decoder source-change and drain flows depend on its sub-state decisions; qbuf paths depend on the vb2-to-driver conversion.

## Risks And Test Signals
`iris_vb2_buffer_to_driver()` assumes `bytesused >= data_offset`; vb2 validation should be verified. Streamon ordering is sensitive: DRC and drain paths require input pause/resume sequencing and internal buffer reallocation before capture restart. Tests should cover decoder DRC, first source-change, drain resume, streamoff with deferred buffers, HFI stop failure, and timestamp metadata preservation on reordered capture output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.h

## Purpose
`iris_common.h` exposes the shared vb2 conversion and stream lifecycle helpers implemented by `iris_common.c`. It is a small interface used by decoder/encoder front-end files and queue operations.

## Important APIs, Types, And Functions
The declarations are `iris_vb2_buffer_to_driver()`, `iris_set_ts_metadata()`, `iris_process_streamon_input()`, `iris_process_streamon_output()`, and `iris_session_streamoff()`. The header forward-declares `struct iris_inst` and `struct iris_buffer`; it relies on including users to have relevant vb2/V4L2 type definitions visible.

## Control Flow
The exported functions sit at V4L2 streamon/streamoff and qbuf boundaries. Decoder and encoder code can call these common helpers after domain-specific validation, avoiding duplicated HFI start/stop, pause/resume, and deferred-buffer completion behavior.

## State And Persistence Behavior
The header itself stores no state, but its API mutates instance state, sub-state, timestamp metadata, buffer attrs, and HFI session state.

## Dependencies And Integration Points
It integrates `iris_common.c` with V4L2 frontend modules, `iris_buffer.c`, HFI command ops, and state management. It is intentionally narrow, making it a stable point for stream lifecycle tests.

## Risks And Test Signals
The main risk is misuse without holding the correct instance or queue locks expected by callers. Tests should exercise the public helpers through normal V4L2 ioctls rather than direct unit calls when possible, because correctness depends on vb2 and mem2mem queue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.c

## Purpose
`iris_core.c` initializes and deinitializes the global Iris hardware core. It owns the ordered boot pipeline for shared HFI queues, VPU power, firmware loading/booting, hardware mode switch, system HFI initialization, and response wait.

## Important APIs, Types, And Functions
`iris_core_init()` is the public boot entry point. `iris_core_deinit()` tears down firmware, VPU power, and HFI queues. `iris_wait_for_system_response()` waits on `core->core_init_done` using the platform `hw_response_timeout` and transitions to `IRIS_CORE_ERROR` on timeout.

## Control Flow
Initialization is serialized by `core->lock`. If the core is already initialized, the function exits successfully; if the core is in error, it returns `-EINVAL`. Otherwise it sets `IRIS_CORE_INIT`, initializes HFI queues, powers on the VPU, loads and authenticates firmware, boots firmware, switches hardware mode, sends HFI core init commands, unlocks, and waits for the system response completion. Error labels unwind in reverse order and return the core to `IRIS_CORE_DEINIT`. Deinit resumes runtime PM, locks the core, unloads firmware, powers off VPU, frees queues, marks deinit, unlocks, and drops PM.

## State And Persistence Behavior
Core state moves among `IRIS_CORE_DEINIT`, `IRIS_CORE_INIT`, and `IRIS_CORE_ERROR`. HFI queue memory, SFR memory, firmware PAS state, VPU power state, and the core-init completion are the persistent resources affected. The init path sets `IRIS_CORE_INIT` before the response arrives, so timeout handling is critical.

## Dependencies And Integration Points
The file depends on runtime PM, `iris_firmware`, VPU common functions, HFI queues, HFI common init, and state definitions. HFI response handlers complete `core_init_done`, making this file tightly coupled to Gen1/Gen2 response parsing.

## Risks And Test Signals
Risks include partial init unwind leaks, response timeout races, and incorrect state after failed firmware boot. Test signals include boot success on each supported platform generation, forced failure at each init step, timeout behavior when firmware does not respond, repeated init/deinit cycles, and runtime-PM reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.h

## Purpose
`iris_core.h` defines the global Iris device/core structure and constants used by all instances and HFI code. It is the central object for hardware resources, V4L2 device registration, platform data, shared queues, command/response ops, power data, and firmware/core state.

## Important APIs, Types, And Functions
`enum domain_type` differentiates `ENCODER` and `DECODER`. `struct icc_info` describes interconnect bandwidth constraints. `struct iris_core` includes device and MMIO references, V4L2 devices and ioctl/vb2 ops, interconnect/clock/reset/power-domain resources, platform data, HFI queue memory, SFR memory, command/message/debug queue descriptors, lock, response buffer, HFI packet/header counters, command/response op tables, core completion, interrupt status, delayed system-error work, instance list, and decoded/encoded firmware capability arrays. Public functions are `iris_core_init()` and `iris_core_deinit()`.

## Control Flow
The core object is allocated and populated by probe/platform code outside this file. HFI generation setup installs `hfi_ops` and `hfi_response_ops`; runtime paths then use the same pointers for both system and session commands. IRQ handling uses `intr_status` and `response_packet`; session lookup walks `instances`.

## State And Persistence Behavior
The structure persists for the device lifetime. It holds long-lived hardware resource handles, runtime state, firmware capabilities copied from platform data, and shared memory pointers that are valid only while the core is initialized.

## Dependencies And Integration Points
The header includes HFI common/queue, platform, resources, and state headers. It is included by firmware, queue, command, response, power, VPU, decoder/encoder, and instance code. Platform data drives almost every core behavior: firmware name, PAS id, queue timeout, caps, buffer tables, UBWC config, and HFI parameter lists.

## Risks And Test Signals
Because `struct iris_core` is broadly shared, lock discipline is important. Tests should look for use-after-deinit of queue pointers, stale HFI ops, response buffer sizing against `IFACEQ_CORE_PKT_SIZE`, and correct capability arrays for encoder and decoder domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.c

## Purpose
`iris_ctrls.c` maps V4L2 controls to Iris platform firmware capability slots and HFI property setters. It initializes per-instance V4L2 controls from platform capability tables, handles dynamic control updates, and translates user-facing values into Gen1/Gen2 firmware payloads.

## Important APIs, Types, And Functions
`iris_ctrls_init()` creates V4L2 controls for all supported capabilities plus min-buffer controls. `iris_session_init_caps()` copies platform decoder and encoder firmware capability tables into `core->inst_fw_caps_dec` and `core->inst_fw_caps_enc`, with special handling for `PIPE`. `iris_set_properties()` applies config params and then calls every capability `set` callback. Setter helpers include generic `iris_set_u32_enum()`/`iris_set_u32()`, stage/pipe, profile/level, Gen1 profile-level packing, header mode, bitrate/peak bitrate, Gen1/Gen2 bitrate mode, entropy mode, min/max/frame QP, QP range, rotation, flip, and intra-refresh period.

## Control Flow
Control IDs are mapped to `enum platform_inst_fw_cap_type` by `iris_get_cap_id()`, and the reverse mapping is used during control creation. `iris_op_s_ctrl()` rejects unsupported controls and rejects non-dynamic controls while the source queue is streaming. Otherwise it marks `CAP_FLAG_CLIENT_SET`, stores the value, and, if streaming, invokes the cap setter. Setter functions call `hfi_ops->session_set_property()` with HFI property id, host flags, port mapping from cap flags/domain, payload type, and payload data.

## State And Persistence Behavior
State is persisted in `inst->fw_caps[]`: current value, min/max, mask/step, flags, HFI property id, and setter callback. Several setters update derived state: peak bitrate may overwrite the cap value, bitrate mode stores `inst->hfi_rc_type`, Gen2 entropy mode may force CAVLC for baseline H.264, QP setters encode client-set enable bits, and AV/control transforms select HFI values.

## Dependencies And Integration Points
The file depends on V4L2 controls, V4L2 mem2mem streaming state, Gen1/Gen2 HFI defines, platform capability definitions, and HFI command ops. It is integrated with streamon via `iris_set_properties()` and with runtime `S_CTRL` ioctls via `iris_ctrl_ops`.

## Risks And Test Signals
Risk areas include mismatched V4L2-to-cap mappings, incorrect dynamic-control flags, inconsistent Gen1/Gen2 HFI value translations, and packed QP bit errors. `iris_set_bitrate()` leaves `max_bitrate` dependent on codec/entropy branches; HEVC currently falls through to entropy-mode selection, so tests should verify HEVC bitrate clipping. Regression tests should cover control enumeration/defaults, invalid values, changing dynamic controls while streaming, bitrate modes, QP min/max/frame interactions, rotation/flip, and intra-refresh behavior during streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.h

## Purpose
`iris_ctrls.h` declares the V4L2 control initialization and firmware property setter interface used by platform capability tables and stream setup.

## Important APIs, Types, And Functions
The header exports `iris_ctrls_init()`, `iris_session_init_caps()`, all named cap setter callbacks, and `iris_set_properties()`. These functions are referenced by platform data through `struct platform_inst_fw_cap.set`, by streamon paths, and by V4L2 control handling.

## Control Flow
Platform data associates firmware capability IDs with setter functions declared here. During session setup, `iris_set_properties()` sends fixed HFI config params and then invokes capability setters. During `S_CTRL`, `iris_op_s_ctrl()` may invoke the same callbacks dynamically.

## State And Persistence Behavior
The declarations mutate `inst->fw_caps[]`, `inst->hfi_rc_type`, stream/session HFI properties, and sometimes current format-derived values. The header does not own state directly.

## Dependencies And Integration Points
It includes `iris_platform_common.h` for capability types and forward-declares `iris_core` and `iris_inst`. It is an integration point between platform capability descriptions, controls, and HFI command generation.

## Risks And Test Signals
The public setter surface is broad and generation-sensitive. Build tests should catch stale declarations when platform tables change; runtime tests should validate that every callback referenced in platform data has the expected payload type for the active HFI generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_ctrls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.c

## Purpose
`iris_firmware.c` loads Qualcomm MDT firmware into reserved memory, authenticates and resets the video subsystem through SCM/PAS, applies trusted-zone content-protection memory settings, unloads firmware, and toggles remote hardware state.

## Important APIs, Types, And Functions
`iris_fw_load()` selects the firmware path from device tree `firmware-name` or platform default, calls the private `iris_load_fw_to_memory()`, authenticates and resets using `qcom_scm_pas_auth_and_reset()`, then applies each `tz_cp_config` through `qcom_scm_mem_protect_video_var()`. `iris_fw_unload()` calls `qcom_scm_pas_shutdown()`. `iris_set_hw_state()` wraps `qcom_scm_set_remote_state()`.

## Control Flow
Firmware loading obtains the first reserved-memory region as a resource, requests the firmware, checks MDT total size against reserved memory size, maps reserved memory with write-combining, calls `qcom_mdt_load()`, unmaps, and releases the firmware. After successful load, PAS auth/reset starts the subsystem. If any TZ memory protection step fails, the code shuts down PAS before returning.

## State And Persistence Behavior
Firmware image state is external to driver heap and lives in reserved memory and SCM-managed subsystem state. The function does not cache firmware data. PAS and TZ memory protection state persist until shutdown or system reset.

## Dependencies And Integration Points
The file depends on Linux firmware APIs, reserved-memory OF APIs, `qcom_mdt_loader`, and Qualcomm SCM calls. `iris_core_init()` invokes `iris_fw_load()` after VPU power-on and before firmware boot/switch-to-hwmode; suspend/resume paths use `iris_set_hw_state()`.

## Risks And Test Signals
`iris_fw_load()` reports firmware download failure as `-ENOMEM` even when lower layers returned another error, which can obscure diagnostics. Tests should cover missing firmware property fallback, too-large firmware image, reserved-memory lookup failure, SCM auth failure, TZ protection failure with PAS shutdown, repeated load/unload, and invalid overly long firmware names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.h

## Purpose
`iris_firmware.h` declares the core firmware lifecycle functions used by the Iris core and power-management paths.

## Important APIs, Types, And Functions
The exported API is `iris_fw_load(struct iris_core *core)`, `iris_fw_unload(struct iris_core *core)`, and `iris_set_hw_state(struct iris_core *core, bool resume)`.

## Control Flow
`iris_core_init()` calls `iris_fw_load()` during boot; `iris_core_deinit()` calls `iris_fw_unload()` during teardown. Runtime suspend/resume uses `iris_set_hw_state()` to inform the remote subsystem state before power transitions.

## State And Persistence Behavior
The API affects PAS authenticated firmware state, reserved memory content, TZ video memory protection, and remote subsystem state. The header owns no direct state.

## Dependencies And Integration Points
The header forward-declares `struct iris_core` and is included by core and HFI common code. Its implementation depends on Qualcomm firmware/SCM infrastructure.

## Risks And Test Signals
Callers must sequence firmware load only after required memory and power resources are available and unload only after sessions/queues are inactive. Suspend/resume and init/deinit tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.c

## Purpose
`iris_hfi_common.c` provides generation-independent HFI support: HFI-to-V4L2 color metadata conversion, system HFI initialization sequencing, IRQ handling, and runtime PM suspend/resume around firmware power collapse.

## Important APIs, Types, And Functions
Color helpers translate HFI color primaries, transfer characteristics, and matrix coefficients into V4L2 colorspace/xfer/ycbcr values. `iris_hfi_core_init()` sends system init, image-version query, and interframe power-collapse setup through `core->hfi_ops`. `iris_hfi_isr()` disables IRQ and wakes the threaded handler. `iris_hfi_isr_handler()` clears VPU interrupt state, dispatches `hfi_response_ops->hfi_response_handler()`, and reenables IRQ if the watchdog does not indicate failure. `iris_hfi_pm_suspend()` prepares power collapse, sets remote state false, and powers off; `iris_hfi_pm_resume()` powers on, sets remote state true, boots firmware, switches hwmode, and re-enables IFPC.

## Control Flow
The top-half IRQ is minimal and always returns `IRQ_WAKE_THREAD`. The threaded handler locks the core only for interrupt clear/runtime-PM marking, then unlocks before response parsing. Suspend first asks firmware/VPU to prepare PC; failure returns `-EAGAIN` after marking PM busy. Resume unwinds by suspending hardware state and powering off on failures.

## State And Persistence Behavior
Core state can be affected indirectly by response handlers and watchdog paths. Runtime PM timestamps, hardware remote-state, VPU power, firmware boot state, and IFPC configuration are mutated. Color helpers are pure mapping functions.

## Dependencies And Integration Points
It depends on runtime PM, firmware state calls, VPU common operations, HFI command/response ops, queue response processing, and V4L2 color enums. Both Gen1 and Gen2 install command/response ops consumed here.

## Risks And Test Signals
Risks include IRQ reenable omissions after watchdog/system error, suspend races while queues contain pending work, and color metadata mismaps. Tests should include interrupt-driven response handling, debug queue draining, watchdog/system-error paths, runtime suspend/resume under active and idle sessions, and color metadata round-trips for common HDR/SDR streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.h

## Purpose
`iris_hfi_common.h` defines the generation-neutral HFI command/response operation tables, packet payload/port/host-flag enums, color metadata enums, subscription data, and common HFI lifecycle APIs.

## Important APIs, Types, And Functions
Important types include `enum hfi_packet_port_type`, `enum hfi_packet_payload_info`, `enum hfi_packet_host_flags`, HFI color enums, `struct iris_hfi_prop_type_handle`, `struct iris_hfi_command_ops`, `struct iris_hfi_response_ops`, and `struct hfi_subscription_params`. Public functions cover HFI color conversion, core init, PM suspend/resume, and IRQ handlers.

## Control Flow
Each platform generation installs an `iris_hfi_command_ops` implementation. Generic core, common streaming, controls, and buffer code call these function pointers without knowing the wire format. The response op is called from the threaded IRQ handler.

## State And Persistence Behavior
The header describes state carried elsewhere: command op pointers in `struct iris_core`, response op pointers, and Gen2 subscription params used for source-change processing. No state is stored in the header itself.

## Dependencies And Integration Points
It includes V4L2 device types and `iris_buffer.h`. It is included by core, controls, HFI queue/command/response, and PM code. The command ops are the main abstraction separating Gen1 packet structs from Gen2 packet headers/sub-packets.

## Risks And Test Signals
Adding a command op requires both generations to implement or callers to handle NULL. Tests should verify that platform-selected HFI generation fills all ops used by common code, especially optional `session_pause` and `session_resume_drain`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1.h

## Purpose
`iris_hfi_gen1.h` declares the setup interface for the Gen1 HFI implementation and its instance allocator.

## Important APIs, Types, And Functions
The header declares `iris_hfi_gen1_command_ops_init()`, `iris_hfi_gen1_response_ops_init()`, and `iris_hfi_gen1_get_instance()`. It forward-declares `struct iris_core` and `struct iris_inst`.

## Control Flow
Platform initialization calls the command and response ops init functions to install Gen1 function tables into `struct iris_core`. Instance creation uses `iris_hfi_gen1_get_instance()` to allocate a plain `struct iris_inst`.

## State And Persistence Behavior
The header owns no state. The Gen1 implementation persists only the generic instance fields and uses Gen1 packet structs transiently on stack or heap.

## Dependencies And Integration Points
This is the generation selection hook used by platform data or probe code. It pairs `iris_hfi_gen1_command.c` with `iris_hfi_gen1_response.c`.

## Risks And Test Signals
If the wrong generation init is selected for hardware, command and response wire formats will mismatch. Probe tests should ensure platform data selects Gen1 only for compatible firmware/hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_command.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_command.c

## Purpose
`iris_hfi_gen1_command.c` implements the Gen1 HFI command operation table. It builds legacy Gen1 packet structs for system init/properties, session open/start/stop/close, buffer queue/release, drain, and session configuration properties.

## Important APIs, Types, And Functions
The file installs `iris_hfi_gen1_command_ops`. Key functions include system packet builders (`sys_init`, image version, IFPC, PC prep), `iris_hfi_gen1_session_open()`, `session_start()`, `session_stop()`, `session_continue()`, input/output/internal buffer queue functions, internal buffer release, drain, and `iris_hfi_gen1_session_set_config_params()`. Property helpers translate common config into Gen1-specific structs such as `hfi_framesize`, `hfi_uncompressed_format_select`, `hfi_buffer_count_actual`, `hfi_multi_stream`, `hfi_buffer_size_actual`, `hfi_framerate`, and encoder rate/QP structs.

## Control Flow
Session open maps V4L2 codec and domain to Gen1 codec/session values, writes `HFI_CMD_SYS_SESSION_INIT`, and waits for response. Decoder/encoder start on output plane sends load-resources then start and sets `IRIS_INST_SUB_LOAD_RESOURCES`. Stop handles decoder streaming flush, decoder loaded-but-not-streaming stop/release, and encoder stop/release, completing queued vb2 buffers with error as needed. Queueing dispatches by `buf->type`: input uses empty-buffer packets, output/DPB uses fill-buffer packets, internals use set-buffers packets. Release sends `HFI_CMD_SESSION_RELEASE_BUFFERS` for non-input buffers and destroys internals after firmware response.

## State And Persistence Behavior
The file mutates `inst->sub_state`, waits on `inst->completion` or `flush_completion`, increments `flush_responses_pending`, and destroys released internal buffers. Gen1 packets are stack or temporary heap allocations. Split-mode decoder maps visible output and DPB streams across `HFI_BUFFER_OUTPUT`/`OUTPUT2`.

## Dependencies And Integration Points
It depends on Gen1 defines, `iris_instance`, `iris_vpu_buffer`, HFI queues, state helpers, controls, and buffer lifecycle code. It is invoked by common streaming and controls through `core->hfi_ops`.

## Risks And Test Signals
Risks include packet size calculation errors for flexible arrays, buffer type translation gaps, stop/flush response accounting, and split-mode stream-id mistakes. Test with decoder and encoder streamon/streamoff, drain, DRC, internal buffer release, unsupported codec, queue-full failure, and all platform config parameter lists. A code-level risk is that `iris_set_profile_level_gen1()` in controls passes `sizeof(u32)` for a `struct hfi_profile_level`; property packing should be verified against firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_defines.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_defines.h

## Purpose
`iris_hfi_gen1_defines.h` is the Gen1 HFI wire-format contract: command/message/event/property IDs, codec and buffer IDs, rate-control values, color formats, packet structs, property payload structs, and response packet layouts.

## Important APIs, Types, And Functions
The file defines Gen1 system/session commands (`HFI_CMD_*`), messages (`HFI_MSG_*`), events, errors, buffer flags, flush values, property IDs, buffer types, codec IDs, picture flags, rate control constants, and H.264 entropy constants. Important structs include generic packet headers, session packets, system get/set property packets, session set buffers/release buffers, empty/fill buffer packets, event notify packets, system/session response packets, image-version property info, format/frame-size/color/DPB/constraint payloads, buffer requirements, bitrate/QP/framerate payloads, fill/empty buffer done packets, and debug/coverage packets.

## Control Flow
Command builders in `iris_hfi_gen1_command.c` populate these structs and write them to the shared HFI command queue. Response parsing in `iris_hfi_gen1_response.c` casts queue data to these layouts, validates minimum sizes, updates instance format/crop/capability state, and completes buffers.

## State And Persistence Behavior
The header itself has no runtime state but defines serialized state shared with firmware. Packet field order and sizes are ABI-sensitive; firmware interprets exactly these layouts.

## Dependencies And Integration Points
It includes Linux types and is included by Gen1 command/response code and controls for Gen1 constants. Platform capability tables reference property IDs from this file for Gen1 hardware.

## Risks And Test Signals
Any struct layout change can break firmware communication. Tests should compare generated packet sizes and field values against known-good traces, validate response parsing for each message type, and compile-check 32-bit/64-bit alignment assumptions where structs include addresses represented as `u32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_response.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_response.c

## Purpose
`iris_hfi_gen1_response.c` parses Gen1 firmware messages, handles system/session errors, sequence changes, buffer completion, flush completion, image-version responses, and debug queue output.

## Important APIs, Types, And Functions
The installed response op is `iris_hfi_gen1_response_handler()`. Important helpers include `iris_hfi_gen1_read_changed_params()`, `iris_hfi_gen1_event_seq_changed()`, system/session error handlers, `iris_hfi_gen1_sys_init_done()`, image-version parsing, `iris_hfi_gen1_session_etb_done()`, `iris_hfi_gen1_session_ftb_done()`, and `iris_hfi_gen1_handle_response()`.

## Control Flow
The handler drains the message queue into `core->response_packet`, dispatches each packet by `hdr->pkt_type`, then drains debug queue. Packet type metadata in `pkt_infos[]` provides minimum-size validation. System init completes `core_init_done`; system property info logs firmware version. Event notify is routed to an instance if its session id matches, otherwise treated as system error. Sequence-change events parse changed properties, update source/destination formats, color metadata, crop, buffer size/min-count, and V4L2 min-buffer control, then trigger output flush and `iris_vdec_src_change()`. ETB done finds source buffers by input tag and completes them. FTB done handles decoder/encoder output, split-mode DPB matching, EOS/drain flags, picture type flags, corrupt/drop errors, and vb2 completion.

## State And Persistence Behavior
The file mutates `core->state`, all instance states on system error, `inst->fmt_src`, `fmt_dst`, `crop`, `fw_min_count`, buffer sizes/counts, V4L2 controls, queue min allocations, buffer attrs, sequence metadata through `iris_vb2_buffer_done()`, `flush_responses_pending`, and completions. Fatal session errors mark vb2 queues errored.

## Dependencies And Integration Points
It depends on Gen1 defines, V4L2 mem2mem, decoder source-change notification, VPU buffer counts, common HFI color conversion, queue read functions, state helpers, and buffer lifecycle functions.

## Risks And Test Signals
Parsing variable changed-parameter payloads has limited bounds checking beyond message minimum size; malformed firmware payloads could advance `data_ptr` incorrectly. Tests should cover all sequence-change property combinations, unsupported bit depth/pic structure, EOS with zero filled length, split-mode DPB return, corrupt/drop flags, flush response counting, image-version packet length validation, and unknown packet handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1_response.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2.h

## Purpose
`iris_hfi_gen2.h` declares the Gen2 HFI setup interface and defines the Gen2-specific instance wrapper that extends `struct iris_inst`.

## Important APIs, Types, And Functions
`struct iris_inst_hfi_gen2` embeds `struct iris_inst`, owns a reusable 4 KiB HFI packet buffer, tracks whether input/output port-settings-change subscriptions were set, stores transient `struct iris_hfi_frame_info`, and holds source/destination `struct hfi_subscription_params`. `to_iris_inst_hfi_gen2()` converts from base instance to wrapper. The exported functions are command/response ops init and Gen2 instance allocation.

## Control Flow
Gen2 session open allocates the reusable packet buffer in the wrapper. Command builders reuse it for one header plus one sub-packet at a time. Response parsing uses wrapper fields to aggregate per-frame info across multi-packet responses and to store subscription values for source-change handling.

## State And Persistence Behavior
The wrapper persists for the session lifetime. `packet` is allocated on open and freed on close or open failure. Subscription params persist across stream setup and source-change responses; `hfi_frame_info` is reset for each response header.

## Dependencies And Integration Points
It includes `iris_instance.h` and relies on `iris_hfi_gen2_packet.h` types through included instance/common headers. Platform generation selection uses these exported init/allocation functions.

## Risks And Test Signals
The embedded-base allocation pattern means Gen2 instances must always be allocated by `iris_hfi_gen2_get_instance()`. Tests should verify close frees the packet buffer, failed open frees it, and no generic free path assumes the allocation is exactly `sizeof(struct iris_inst)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_command.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_command.c

## Purpose
`iris_hfi_gen2_command.c` implements the Gen2 HFI command operation table. It builds Gen2 header/sub-packet commands and properties for system init, session open/close/start/stop/pause/resume/drain, property configuration, subscribe mode, and buffer queue/release.

## Important APIs, Types, And Functions
System functions allocate packet buffers sized for init, no-payload, or IFPC messages and call packet helpers. Port mapping helpers convert V4L2 planes and Iris buffer types to HFI ports. Property setters cover raw/bitstream resolution, crop offsets, bit depth, coded frames, min output count, POC, colorspace, profile/level/tier, OPB, color format, linear stride/scanline, frame rate, AV1 film grain, and super-block. Session functions include `session_open()`, codec/default-header setup, subscribe-mode helpers, start/stop/pause/resume/drain, buffer conversion, COMV count setup, queue, and release.

## Control Flow
Open allocates a 4 KiB packet buffer, sends `HFI_CMD_OPEN` with response/interrupt flags, then sends codec and decoder default-header properties. Start first subscribes to port-setting-change and property notifications, then sends `HFI_CMD_START` for the plane. Subscribe-change stores input PSC params, and for output PSC copies source params to destination then sends current property values back on the raw port. Buffer queue converts `struct iris_buffer` into `struct iris_hfi_buffer`, aligns decoder bitstream size to 256, sets non-secure callback flag, optionally sets AV1 COMV count, and sends `HFI_CMD_BUFFER`.

## State And Persistence Behavior
The file updates Gen2 wrapper booleans `ipsc_properties_set`/`opsc_properties_set`, `src_subcr_params`, `dst_subcr_params`, and the reusable packet buffer. It also reuses generic state through completions, `inst->sub_state`, buffer attrs, timestamps, and `inst->hfi_rc_type` set by controls.

## Dependencies And Integration Points
It depends on Gen2 packet helpers/defines, common HFI ops, platform config/property arrays, format/crop/compose fields, VPU buffer counts, and controls. It is consumed through `core->hfi_ops` by common stream and buffer paths.

## Risks And Test Signals
The reusable packet buffer assumes all command/property packets fit in 4 KiB; platform arrays used for subscribe payloads should stay within the fixed local `payload[32]`. `iris_hfi_gen2_get_port_from_buf_type()` maps `BUF_PERSIST` to `HFI_PORT_NONE`, but response validation only accepts `HFI_PORT_NONE` for persist after an early port check that rejects non-bitstream/raw ports; release handling should be tested for persist buffers. Tests should cover every codec-specific config list, rotation/crop resolution packing, AV1 COMV count, subscribe idempotence, open failure cleanup, drain resume, and internal buffer release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h

## Purpose
`iris_hfi_gen2_defines.h` defines the Gen2 HFI numeric protocol: command ranges, property IDs, error/info ranges, codec IDs, color formats, picture types, buffer types, host/firmware buffer flags, packet firmware flags, and debug header.

## Important APIs, Types, And Functions
Key constants include command IDs (`HFI_CMD_INIT`, `OPEN`, `START`, `BUFFER`, `SUBSCRIBE_MODE`, `SETTINGS_CHANGE`, `PAUSE`), property IDs (`HFI_PROP_*` for image version, UBWC, codec, resolution, crop, profile/level/tier, rate control, QP, rotation/flip, color info, AV1 features, OPB, COMV), error ranges, information flags, rate-control enum values, sequence-header modes, rotation/flip enums, codec types, picture types, buffer types, host buffer flags, firmware buffer flags, and packet flags.

## Control Flow
Command builders use these IDs as packet `type` values. Response handlers use begin/end ranges to dispatch packets to system error, session error, info, property, and command handlers. Buffer type and flag enums drive conversion to/from `enum iris_buffer_type` and V4L2 buffer flags.

## State And Persistence Behavior
The header has no mutable state but defines serialized values persisted in command queues and firmware responses. The begin/end range constants are part of dispatch logic and therefore ABI-sensitive.

## Dependencies And Integration Points
It includes Linux types and is included by Gen2 packet, command, response, and controls code. Platform capability tables use property IDs from this file for Gen2 hardware.

## Risks And Test Signals
Numeric mismatches break firmware communication. Tests should include packet trace comparison for common commands, response dispatch coverage for each range, and picture/error/info flag translation. Any new Gen2 property must be added to setters and response subscription handling as needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c

## Purpose
`iris_hfi_gen2_packet.c` provides low-level Gen2 packet construction and V4L2-to-HFI color metadata packing. It hides the details of creating a Gen2 `iris_hfi_header` plus one or more `iris_hfi_packet` sub-packets.

## Important APIs, Types, And Functions
Color helpers map V4L2 colorspace, transfer function, and YCbCr encoding to HFI primaries/transfer/matrix values. `iris_hfi_gen2_get_color_info()` packs matrix, transfer, primaries, description-present, full-range, video-format, and signal-present bits. Packet helpers create headers and packets, and public builders emit system init, image-version query, session command, session property, IFPC property, and PC prep command.

## Control Flow
System init creates one header and eight sub-packets: `HFI_CMD_INIT` plus UBWC platform configuration properties. Image-version uses a get-property flag with no payload. Session command/property builders create one header and one packet in the instance's reusable buffer. Header and packet IDs are incremented from `core->header_id` and `core->packet_id`.

## State And Persistence Behavior
The functions mutate only caller-provided packet memory and increment core header/packet counters. UBWC values are read from immutable platform data. Generated packets are transient until written into the HFI command queue.

## Dependencies And Integration Points
It depends on Gen2 defines, common HFI host flags/payload enums, Gen2 instance wrapper, and platform UBWC configuration. Gen2 command ops call these helpers for all wire-format construction.

## Risks And Test Signals
There is no explicit buffer-size parameter in `iris_hfi_gen2_create_packet()`, so callers must allocate enough space. Tests should assert system init packet size equals expected constants, packet counters increment monotonically, payload bytes are copied correctly, and color-info bit packing round-trips with Gen2 response parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h

## Purpose
`iris_hfi_gen2_packet.h` declares the Gen2 packet wire structs and packet-building/color-packing API.

## Important APIs, Types, And Functions
`struct iris_hfi_header` is the top-level Gen2 packet header with total size, session id, header id, reserved fields, and packet count. `struct iris_hfi_packet` describes each sub-packet with size, type, flags, payload type, port, packet id, reserved fields, and flexible payload. `struct iris_hfi_buffer` is the serialized firmware buffer descriptor containing HFI buffer type, index, 64-bit base address, offsets, sizes, timestamp, flags, and reserved fields. The API exports V4L2-to-HFI color helpers, color-info packing, and packet builders for system/session commands and properties.

## Control Flow
Command code fills `iris_hfi_buffer` from `struct iris_buffer`, then asks packet helpers to wrap it in a Gen2 command. Response code casts payloads back to `iris_hfi_buffer` after validating payload size.

## State And Persistence Behavior
The structs represent shared-queue wire state. The header does not store runtime state, but its layouts must remain stable for firmware compatibility.

## Dependencies And Integration Points
It includes Gen2 defines and forward-declares `struct iris_core`. It is used by Gen2 command and response files and indirectly by the Gen2 instance wrapper.

## Risks And Test Signals
ABI risks include struct padding, flexible payload sizing, and address width assumptions. Build and trace tests should verify sizes and field offsets expected by firmware, especially for `iris_hfi_buffer` on different architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_response.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_response.c

## Purpose
`iris_hfi_gen2_response.c` parses Gen2 response headers/sub-packets, dispatches system/session errors, info, properties, commands, source-change events, buffer completions, internal buffer releases, image-version responses, and debug messages.

## Important APIs, Types, And Functions
The installed op is `iris_hfi_gen2_response_handler()`. Key helpers validate headers and packets, translate HFI buffer/picture/info flags to driver flags, handle session info/error/system error/init/close/stop/drain, handle input/output/internal buffer returns, dequeue completed vb2 buffers, read subscription params into V4L2 formats/caps, handle source change, handle properties, parse image version, and flush debug queue.

## Control Flow
The response handler first checks VPU watchdog and synthesizes a system error on watchdog timeout. It drains message packets from the queue, validates each Gen2 header and sub-packet against `IFACEQ_CORE_PKT_SIZE`, then dispatches to system or session handling based on `hdr->session_id`. System handling iterates packets by range and completes `core_init_done` for successful init. Session handling finds the instance, clears transient frame info, initializes source-change defaults when a settings-change packet appears, then makes ordered passes over session-error, info, property, and command ranges. If any buffer packet was handled, it completes all Iris buffers marked `DEQUEUED`.

## State And Persistence Behavior
The file mutates core error state, all instance states on system error, Gen2 `hfi_frame_info`, subscription params, source/destination V4L2 formats, crop, firmware caps, output buffer min-count/size, V4L2 min-buffer controls, queue min allocation, buffer attrs, payload/timestamp/flags, completions, and drain/DRC sub-states. Internal release responses remove and free internal DMA buffers.

## Dependencies And Integration Points
It depends on Gen2 packet/defines, V4L2 mem2mem, decoder source-change notification, VPU watchdog, VPU buffer counts, common HFI color conversion, queue read functions, state helpers, and `iris_vb2_buffer_done()`.

## Risks And Test Signals
Validation is stronger than Gen1 but still trusts `hdr->num_packets` after checking each packet stays inside the fixed response buffer. `iris_hfi_gen2_is_valid_hfi_port()` returns false for `HFI_PORT_NONE` before considering persist-buffer allowance, which may affect persist release responses. Tests should cover watchdog error, malformed packet sizes, multi-packet ordering where info/properties precede buffer command, no-output/corrupt/overflow picture flags, source-change subscription properties, AV1 film grain/super-block updates, zero-sized output frames, last/PSC-last flags, and internal buffer release for every internal type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen2_response.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.c

## Purpose
`iris_hfi_queue.c` implements the shared host-firmware queue transport. It allocates queue/SFR DMA memory, initializes command/message/debug queue headers, writes command packets with wraparound handling, reads firmware packets, raises hardware interrupts, and frees queue resources.

## Important APIs, Types, And Functions
Private helpers are `iris_hfi_queue_write()`, `iris_hfi_queue_read()`, queue header setup/init/deinit functions. Public functions are `iris_hfi_queues_init()`, `iris_hfi_queues_deinit()`, `iris_hfi_queue_cmd_write_locked()`, `iris_hfi_queue_cmd_write()`, `iris_hfi_queue_msg_read()`, and `iris_hfi_queue_dbg_read()`.

## Control Flow
Queue writes calculate empty space from read/write indices in bytes, reject insufficient space, copy the packet linearly or with wraparound, issue memory barriers before and after updating `write_idx`, then command writes raise a VPU interrupt. Unlocked command writes wrap runtime PM resume/get, `core->lock`, locked write, and autosuspend. Queue reads detect empty queues, set `rx_req`, validate read pointer and packet size, copy linearly or with wraparound if the packet fits `IFACEQ_CORE_PKT_SIZE`, update `read_idx`, and return `-EBADMSG` for oversized packets. Queue init allocates one aligned DMA block for table plus three 800 KiB queues and a separate 4 KiB SFR block.

## State And Persistence Behavior
Shared DMA memory persists while the core is initialized. Queue headers hold firmware-visible `read_idx`, `write_idx`, request bits, watermarks, status, and queue metadata. `core->iface_q_table_vaddr/daddr`, `sfr_vaddr/daddr`, and per-queue descriptors are valid until deinit.

## Dependencies And Integration Points
It depends on runtime PM, VPU interrupt helpers, DMA allocation, `iris_core`, and queue structs. All HFI command implementations write through this file, and all response handlers read message/debug queues through it.

## Risks And Test Signals
Queue-full handling converts any write failure to `-ENODATA`, losing the original reason. Pointer arithmetic uses `void *` extensions in read paths and should be compiler-checked. Tests should cover wraparound writes/reads, empty queue rx request behavior, oversized packet handling, command write in error/deinit core states, DMA allocation failure cleanup, runtime-PM balance, and debug queue draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.h

## Purpose
`iris_hfi_queue.h` defines the host-firmware shared queue layout, sizing constants, queue headers, queue table header, per-queue descriptor, and queue API.

## Important APIs, Types, And Functions
Constants define maximum queued buffers, maximum parallel sessions, default queue header type, maximum packet size, SFR size, per-queue size, and queue ids. `struct iris_hfi_queue_header` mirrors firmware-visible queue metadata and indices. `struct iris_hfi_queue_table_header` describes the table plus three queue headers. `struct iris_iface_q_info` holds the driver-side qhdr pointer, device address, and kernel virtual address. Public functions initialize/deinitialize queues and write/read command/message/debug queues.

## Control Flow
The memory layout comment documents a table header followed by command, message, and debug queue headers and three queue data areas. Queue ids index both header array and data offsets in `iris_hfi_queue.c`.

## State And Persistence Behavior
Queue header fields are shared mutable state between host and firmware. SFR memory gives firmware a place to store subsystem failure reason data.

## Dependencies And Integration Points
The header forward-declares `struct iris_core` and is included by core and HFI queue users. `IFACEQ_CORE_PKT_SIZE` from `iris_core.h` bounds response packet copies.

## Risks And Test Signals
Sizing constants drive DMA allocation and packet validation. Tests should validate total queue allocation size, queue alignment, header offsets, and compatibility with firmware expectations for 16 sessions and 64 buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_instance.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_instance.h

## Purpose
`iris_instance.h` defines the per-open video session state shared across decoder, encoder, HFI, controls, buffers, power, and V4L2 queue code.

## Important APIs, Types, And Functions
It defines default dimensions, output codec format type enum, capture raw format type enum, `struct iris_fmt`, and `struct iris_inst`. The instance holds list linkage to the core, session id, queue and forward/reverse locks, V4L2 file handle, source/destination formats, control handler, domain, crop/compose rectangles, completions, flush response count, firmware caps, buffer arrays, firmware min count, instance state/sub-state, once-per-session flag, max input data size, power and interconnect votes, mem2mem device/context, output/capture sequence counters, timestamp metadata ring, codec, last-buffer flag, frame/operating rates, HFI rate-control type, and encoder raw/scaled dimensions.

## Control Flow
Instances are allocated by generation-specific allocators, initialized by decoder or encoder code, attached to `core->instances`, and then passed through all V4L2 operations. HFI commands use `session_id`, formats, crop/compose, caps, buffers, state, and completions. HFI responses find instances by session id and mutate buffer/state/format fields under `inst->lock`.

## State And Persistence Behavior
The structure persists for one file/session lifetime. It is the main persistence boundary for stream configuration, controls, queue state, firmware/session state, and power votes. The timestamp metadata ring bridges output timestamps/timecode into capture completions.

## Dependencies And Integration Points
It includes V4L2 controls, `iris_buffer`, `iris_core`, and utility types. It is consumed by nearly every Iris source file. Gen2 embeds this struct in a larger wrapper; Gen1 allocates it directly.

## Risks And Test Signals
Locking is split between `ctx_q_lock` for queue ioctls and `lock` for forward/reverse thread serialization; races should be tested around qbuf/streamoff/IRQ completion. Since many fields are updated by both userspace ioctl paths and firmware response paths, tests should stress concurrent streamoff, DRC, drain, close, and system-error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_instance.h -->
