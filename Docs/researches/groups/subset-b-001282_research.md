# subset-b-001282 SCMI Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/protocols.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/protocols.h

Purpose: This internal SCMI protocol header defines the common in-kernel contracts used by protocol implementations in `drivers/firmware/arm_scmi`. It supplies SCMI revision helpers, common command IDs, transfer state, protocol handles, iterator helpers, fast-channel descriptors, core xfer callbacks, and the protocol registration macros used by reset, sensor, voltage, system, and other protocols.

Important APIs/types/functions: `struct scmi_xfer` is the central message lifecycle object, with packed header, tx/rx buffers, completions, pending/free list node, refcount, busy/state flags, raw-mode flags, lock, and transport private pointer. `struct scmi_protocol_handle` exposes a device, negotiated version, `xops`, `hops`, and protocol private-data setters/getters to each protocol implementation. `struct scmi_iterator_state` and `struct scmi_iterator_ops` provide a generic pattern for multi-part firmware replies. `struct scmi_proto_helpers_ops` exposes extended-name lookup, iterator creation/run, message support checks, fast-channel setup/ringing, and max message size. `struct scmi_xfer_ops` is the protocol-facing core send API. `struct scmi_protocol` is the registration descriptor, including standard/vendor protocol identity, ops, events, supported version, and optional vendor matching fields.

Control flow: Protocol implementations receive a `scmi_protocol_handle` during instance init, allocate private state, issue messages through `ph->xops`, optionally use `ph->hops` for common parsing features, then publish operations through `ph->set_priv()` and the static `scmi_protocol` descriptor. `DEFINE_SCMI_PROTOCOL_REGISTER_UNREGISTER()` emits init/exit registration wrappers for built-in SCMI protocol registration.

State and persistence: The header defines runtime-only state. Transfer persistence is limited to core-managed xfer pools and pending hash/list nodes. Protocol private state is attached to a handle through callbacks and normally allocated with devres in implementation files. There is no on-disk persistence.

Dependencies and integration points: It depends on Linux device, module, completion, refcount, spinlock, hash/list, bitfield, unaligned, and exported SCMI public protocol headers. It is consumed by protocol implementations and indirectly by transports and notification support. The revision macros are shared by all protocol version gates.

Risks and edge cases: Correctness depends on protocol implementations respecting the `xops` contract and not forging protocol IDs. `scmi_xfer` state transitions are documented but enforced in core code outside this header; races are mitigated by refcounts, atomics, and `lock`, but misuse can cause reuse-after-timeout or stale response handling. Iterator users must set max resources and parse response lengths defensively.

Test signals: Build coverage should confirm all protocol descriptors compile against this contract. Runtime signals include successful SCMI protocol registration, version negotiation, multi-part iterator consumers parsing sensor/voltage responses, raw-mode flags not leaking into normal transactions, and no refcount/list corruption under timeout and delayed-response tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/protocols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.c

Purpose: This file implements the SCMI quirk framework. It defines named firmware/workaround static keys, parses activation constraints, stores quirk descriptors in a runtime hash table, and enables matching quirks after the SCMI server advertises vendor, sub-vendor, implementation version, and optional compatible strings.

Important APIs/types/functions: `struct scmi_quirk` stores the quirk name, vendor/sub-vendor match strings, implementation version range, parsed start/end values, static key pointer, hash node/key, enabled flag, and optional compatible list. `DEFINE_SCMI_QUIRK()` and `DEFINE_SCMI_QUIRK_EXPORTED()` create static-key-backed descriptors. Current global quirks are `clock_rates_triplet_out_of_spec` and exported `perf_level_get_fc_force` style support via declarations in the header. `scmi_quirk_signature()` builds a case-insensitive hash from vendor/sub-vendor. `scmi_quirk_range_parse()` accepts `NULL`, `X`, `X-`, `-X`, and `X-Y`. `scmi_quirks_initialize()` parses and hashes the static table. `scmi_quirks_enable()` walks fallback match signatures and calls `static_branch_enable()`.

Control flow: Initialization iterates `scmi_quirks_table`, validates version ranges, computes a hash key for each descriptor, and inserts it into `scmi_quirks_ht`. At platform probe time, `scmi_quirks_enable()` tries increasingly generic match keys from full vendor/sub-vendor to wildcard signatures, filters by range, compatible list, prior enablement, and exact hash key, then enables the quirk static branch.

State and persistence: Quirk state is in static descriptors and a read-mostly hash table. `enabled` prevents repeated static key enables. Parsed ranges and hash keys persist for the life of the module/kernel. No data is persisted outside memory.

Dependencies and integration points: It depends on static keys, device tree compatibility matching, kernel string hashing, `kstrtouint()`, and `quirks.h`. Local SCMI code associates workaround snippets with a quirk using `SCMI_QUIRK(name, block)`, so the framework integrates by making those snippets nearly free when disabled.

Risks and edge cases: Hash collisions are explicitly handled by rechecking `hkey`, but quirk match semantics can still be surprising because generic fallback signatures can match descriptors with `NULL` vendor/sub-vendor. Bad range strings skip registration. `dev_dbg()` in enablement references `quirk->compats[0]`, `vendor`, and `sub_vendor_id`; nullable values are acceptable with `%s` only if kernel formatting handles NULL. Compatible-list matching makes quirk activation dependent on global machine compatibles, not just the SCMI node.

Test signals: Boot logs should show registered quirks under dynamic debug and "Enabling SCMI Quirk" only for intended firmware. Unit-style tests can cover all range string forms and inverted ranges. Platform tests should verify enabled static branches change behavior in clock/perf code and remain disabled on nonmatching vendor/version/compatible combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.h

Purpose: This header exposes the SCMI quirk static-key API to the rest of the SCMI stack while compiling to no-op helpers when `CONFIG_ARM_SCMI_QUIRKS` is disabled.

Important APIs/types/functions: `DECLARE_SCMI_QUIRK()` declares global static keys. `SCMI_QUIRK(_qn, _blk)` executes the provided block only when the named static branch is enabled; in disabled builds the block is compiled but never executed through an `if (0)` construct. `scmi_quirks_initialize()` and `scmi_quirks_enable()` are real functions under the config and inline no-ops otherwise. Declared quirks are `clock_rates_triplet_out_of_spec` and `perf_level_get_fc_force`.

Control flow: SCMI core calls initialization and enablement hooks unconditionally. The header hides build-time configuration by making those hooks no-op without quirk support. Workaround sites invoke `SCMI_QUIRK()` around small code blocks and rely on static branch patching for low overhead.

State and persistence: The header itself holds no state. With quirks enabled, state lives in `quirks.c` static keys and descriptors; with quirks disabled, no state is retained.

Dependencies and integration points: It includes Linux static-key and type headers. It must stay synchronized with quirk definitions in `quirks.c`: each defined quirk needs a declaration here so code snippets can reference its static key.

Risks and edge cases: The comment says "delarations", a harmless typo. More importantly, missing declarations cause compile failures at use sites, while stale declarations without a descriptor would leave an unreachable static key. The disabled-build macro still type-checks the block, which is useful but means referenced symbols must exist even when runtime support is off.

Test signals: Compile both `CONFIG_ARM_SCMI_QUIRKS=y` and disabled configurations. Runtime test signals are static branch enablement for matching platforms and absence of quirk side effects when config is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/quirks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.c

Purpose: This file implements SCMI Raw mode, a debugfs testing interface that lets userspace inject bare little-endian SCMI messages and snoop replies, notifications, and error replies through the normal SCMI core and active transport. It is intended for backend/server testing and CI, not production.

Important APIs/types/functions: `struct scmi_raw_mode_info` owns the raw instance, transport descriptor, queue array, optional per-channel queues, waiter pools, workqueue, debugfs root, and devres group. `struct scmi_raw_queue` provides free buffers, queued messages, spinlocks, and waitqueue. `struct scmi_xfer_raw_waiter` tracks xfers deferred for completion waiting. `struct scmi_raw_buffer` stores serialized raw messages. `struct scmi_dbg_raw_data` is per-open debugfs file state. Public hooks are `scmi_raw_mode_init()`, `scmi_raw_mode_cleanup()`, `scmi_raw_message_report()`, and `scmi_raw_error_report()`.

Control flow: Initialization allocates reply/notification/error queues, optional per-channel xarray queues, waiters, and a high-priority workqueue, then creates debugfs files `message`, `message_async`, `message_poll`, `message_poll_async`, `notification`, `errors`, `reset`, and per-channel variants. A write accumulates exactly one raw message, builds an xfer from the supplied header/payload, registers it as in-flight with retry support for reused sequence numbers, selects a channel, sends it through the transport, and queues a waiter. The deferred worker waits for synchronous completion, marks tx done, optionally waits for async delayed response, then releases the xfer and waiter. The normal SCMI RX path calls `scmi_raw_message_report()` to serialize a reply/notification into a raw queue. Error paths call `scmi_raw_error_report()` to fetch payload into a temporary xfer and enqueue it as an error report.

State and persistence: Raw mode keeps bounded in-memory queues sized by `tx_max_msg`. Reply queues require userspace to read messages to free buffers; notification and error queues overwrite the oldest buffer when exhausted. Per-open debugfs state holds partially written tx messages and current rx message position. No state persists beyond debugfs lifetime.

Dependencies and integration points: It depends on debugfs, xarray, workqueues, SCMI core raw xfer helpers from `common.h`, transport ops from `struct scmi_desc`, and tracepoints. It integrates with the core by receiving RX/error hooks and by setting `SCMI_XFER_FLAG_IS_RAW`/`SCMI_XFER_FLAG_CHAN_SET` behavior through core helpers.

Risks and edge cases: Userspace controls tokens and can create concurrency hazards; the implementation retries in-flight registration but cannot prevent poor sequence selection. Polling is honored only when the transport supports it. A send failure after waiter allocation must release the waiter and xfer correctly. Reply buffer exhaustion drops replies loudly, which signals broken tests. Notification floods can overwrite older data by design. The debugfs write logic treats the first write count as the full message size, so interrupted or partial writes require careful userspace behavior.

Test signals: With raw mode enabled, debugfs should expose global and per-channel files. Tests should inject sync, async, polling, and per-channel messages; verify EOF per message boundary; verify `poll()` wakes on replies/notifications/errors; force timeout/late-reply paths; and confirm reset flushes queues. Coexistence tests should check notification flood behavior and absence of normal driver interference according to config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.h -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.h

Purpose: This header declares the raw-mode queue IDs and the raw-mode hooks used by the SCMI core and transports to initialize, tear down, and report raw messages.

Important APIs/types/functions: The queue enum defines `SCMI_RAW_REPLY_QUEUE`, `SCMI_RAW_NOTIF_QUEUE`, `SCMI_RAW_ERRS_QUEUE`, and `SCMI_RAW_MAX_QUEUE`. `scmi_raw_mode_init()` creates a raw-mode instance for an SCMI handle, debugfs root, instance ID, transport channels, descriptor, and max in-flight count. `scmi_raw_mode_cleanup()` tears it down. `scmi_raw_message_report()` serializes normal replies/notifications. `scmi_raw_error_report()` serializes unexpected or timed-out replies.

Control flow: Core code can keep the opaque pointer returned by init and pass it back into report/cleanup functions. Queue selection and debugfs behavior are implemented in `raw_mode.c`.

State and persistence: The header has no state; the returned opaque pointer represents runtime state owned by `raw_mode.c`.

Dependencies and integration points: It includes `common.h`, so users see SCMI handle, channel, descriptor, and xfer types. It is an integration boundary between generic core RX/error handling and optional debug raw mode.

Risks and edge cases: Callers must pass the correct queue index and channel ID. The opaque pointer can be NULL only where implementation tolerates it; cleanup and report hooks guard against NULL, but misuse before initialization loses reports.

Test signals: Build tests must cover raw mode enabled/disabled callers. Runtime tests should verify that core RX hooks pass replies to the reply queue and notifications to the notification queue using these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/reset.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/reset.c

Purpose: This file implements the SCMI Reset protocol agent. It discovers reset domains, exposes reset/assert/deassert operations to SCMI clients, and wires reset-issued notifications into the SCMI notification framework.

Important APIs/types/functions: `struct reset_dom_info` caches per-domain async reset support, notification support, latency, and name. `struct scmi_reset_info` stores domain count, whether `RESET_NOTIFY` exists, and the domain array. Protocol ops include `scmi_reset_num_domains_get()`, `scmi_reset_name_get()`, `scmi_reset_latency_get()`, `scmi_reset_domain_reset()`, `scmi_reset_domain_assert()`, and `scmi_reset_domain_deassert()`. Notification ops include `scmi_reset_notify_supported()`, `scmi_reset_set_notify_enabled()`, and `scmi_reset_fill_custom_report()`.

Control flow: `scmi_reset_protocol_init()` allocates private state, calls `PROTOCOL_ATTRIBUTES`, allocates one descriptor per domain, and retrieves each domain's attributes/name/latency. Reset requests validate the domain, add the asynchronous flag for autonomous resets when supported, send `RESET`, and either wait for delayed response or synchronous completion. Notification enablement sends `RESET_NOTIFY` per domain and report filling decodes agent, domain, and reset state.

State and persistence: Domain metadata is cached in devm-managed memory for the protocol instance. Notification enablement state is managed by the generic notification core and firmware. No persistent storage is used.

Dependencies and integration points: It depends on `protocols.h`, `notify.h`, Linux module support, and public `linux/scmi_protocol.h` reset types. It registers as `SCMI_PROTOCOL_RESET` with ops and `reset_protocol_events`, so reset controller drivers can consume it.

Risks and edge cases: Domain lookup returns `-EINVAL` for out-of-range IDs. Per-domain attribute failures during init are ignored by the loop, leaving default zeroed entries, so missing firmware data can surface later as empty names or unsupported flags. Extended name lookup failures are intentionally nonfatal. Async reset delayed-response validation is delegated to core transport behavior.

Test signals: Firmware test cases should cover zero/multiple domains, extended names, latency `U32_MAX` normalization to zero, sync and async reset commands, assert/deassert, invalid domain IDs, `RESET_NOTIFY` absence, and decoding of reset-issued reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/scmi_power_control.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/scmi_power_control.c

Purpose: This SCMI driver consumes System Power notifications and turns platform-originated graceful shutdown, reboot, and suspend requests into Linux system transitions.

Important APIs/types/functions: `enum scmi_syspower_state` tracks idle, in-progress, and rebooting. `struct scmi_syspower_conf` stores device pointer, state mutex, requested transition, SCMI userspace notifier, reboot notifier, delayed forceful work, and suspend work. Key functions are `scmi_userspace_notifier()`, `scmi_request_graceful_transition()`, `scmi_reboot_notifier()`, `scmi_forceful_work_func()`, `scmi_request_forceful_transition()`, `scmi_syspower_probe()`, and `scmi_system_power_resume()`.

Control flow: Probe acquires the SCMI System protocol, allocates driver state, initializes suspend work, and registers an event notifier for `SCMI_EVENT_SYSTEM_POWER_STATE_NOTIFIER`. On notification, the driver rejects unsupported states and forceful platform requests, ignores duplicate or late events, records the requested transition, and invokes orderly poweroff/reboot or schedules suspend. If firmware provided a timeout for graceful shutdown, it registers a reboot notifier and schedules delayed work at 75 percent of the timeout; if a matching reboot begins, the delayed work is canceled, otherwise the worker unregisters the notifier and calls the kernel forceful transition path.

State and persistence: State is per driver instance and protected by `state_mtx`. The SCMI core is expected to instantiate only one System Power device. Resume resets state to idle. No state is persisted across reboot or suspend beyond normal kernel memory.

Dependencies and integration points: It uses the SCMI bus driver model, SCMI notify ops, reboot notifier chain, orderly power APIs, `pm_suspend()`, delayed work, and emergency sync in built-in builds. It integrates with `system.c`, which supplies the protocol event decoder.

Risks and edge cases: Forceful notifications from firmware are ignored by design. The timeout path unregisters the reboot notifier while holding state mutex; the code comments call this out to avoid deadlock. If userspace is unavailable, `orderly_poweroff(true)` can still force shutdown. Duplicate notifications are ignored once state is not idle. Suspend is scheduled asynchronously and does not use the forceful timeout mechanism.

Test signals: Use synthetic System Power notifications for shutdown, cold reset, warm reset, suspend, unsupported states, duplicate events, and forced notifications. Verify reboot notifier cancellation, delayed forceful fallback timing, resume resetting state, and that only one SCMI system-power driver binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/scmi_power_control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/sensors.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/sensors.c

Purpose: This file implements the SCMI Sensor protocol agent. It discovers sensors, update intervals, axes, scalar/axis attributes, supports synchronous/asynchronous readings, configuration, trip points, and notification reports for trip and continuous update events.

Important APIs/types/functions: `struct sensors_info` stores protocol-wide notification command support, sensor count, max requests, optional register address/size, and the sensor descriptor array. Protocol ops are `count_get`, `info_get`, `trip_point_config`, `reading_get`, `reading_get_timestamped`, `config_get`, and `config_set`. Iterator helpers parse update intervals, axis descriptors, axis extended names, and sensor descriptors. Event handlers are `scmi_sensor_notify_supported()`, `scmi_sensor_set_notify_enabled()`, and `scmi_sensor_fill_custom_report()`.

Control flow: Init reads `PROTOCOL_ATTRIBUTES`, detects optional trip/update notify commands, allocates descriptors, then iterates `SENSOR_DESCRIPTION_GET`. Each descriptor parses async read, trip points, update notifications, timestamp support, scalar extended attributes, scale/type, v2 or v3 update interval format, optional extended name, and optional axes. Axis parsing uses nested iterators and may fetch extended axis names. Read calls validate the sensor ID, choose async delayed-response or synchronous flow, and parse scalar or timestamped multi-axis results. Notification enablement maps event IDs to trip or continuous update commands, and report filling decodes variable-size update payloads based on sensor axis count.

State and persistence: Sensor metadata, intervals, axis descriptors, and cached config values live in devm-managed private state. Update interval descriptors use a preallocated pool when possible and devm allocation when larger. Notification enablement is runtime state in firmware/core. No persistent storage exists.

Dependencies and integration points: It depends on `protocols.h`, `notify.h`, SCMI public sensor types, generic iterator helpers, extended-name helper, and xfer operations. Consumers are hwmon/IIO/thermal or other SCMI sensor clients through `scmi_sensor_proto_ops`.

Risks and edge cases: Many replies are variable length and version-dependent. The code caps axes at `SCMI_MAX_NUM_SENSOR_AXIS`, tolerates missing update intervals, and treats extended name failures as nonfatal. `scmi_sensor_config_get()` reads a 64-bit value into a 32-bit output via `get_unaligned_le64()`, which is suspicious and should be tested against expected firmware layouts. Continuous update report parsing trusts the preallocated max report size and sensor axis count after validating sensor ID. Firmware bugs in reserved v3 bits on v2 platforms could mislead parsing, as comments note.

Test signals: Test v2 and v3 firmware descriptors, segmented and listed intervals, scalar and multi-axis sensors, extended names, async and sync readings, timestamped readings, invalid IDs/counts, missing optional commands, trip point config, notification enable/disable, and malformed variable-length payloads. KASAN/UBSAN and fault-injection tests are valuable around descriptor size calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/shmem.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/shmem.c

Purpose: This file implements shared-memory transport helpers for SCMI SMT-style transports. It prepares tx messages in the SCMI shared memory layout, fetches responses/notifications, clears channels, polls completion, maps device-tree shmem regions, and chooses IO copy methods.

Important APIs/types/functions: `struct scmi_shared_mem` models the SCMI shared memory header and payload. `shmem_tx_prepare()` waits for a free channel, writes channel status, flags, length, header, and payload. `shmem_fetch_response()` reads status and response payload. `shmem_fetch_notification()` reads notification payload without status. `shmem_clear_channel()`, `shmem_poll_done()`, `shmem_channel_free()`, and `shmem_channel_intr_enabled()` expose state checks. `shmem_setup_iomap()` validates the DT `shmem` phandle, resource size, compatibility, maps it, and selects 32-bit or default IO copy ops. `scmi_shared_mem_operations_get()` exports the operation table.

Control flow: Transports call `setup_iomap()` at channel setup. On send, transports call `tx_prepare()` before ringing a mailbox/SMC/OP-TEE doorbell. On RX, they read the header then fetch response or notification. After P2A processing, transports clear the channel and may signal completion to firmware.

State and persistence: Shared memory itself is firmware/OS shared runtime state. The helper keeps no global mutable state. IO ops are static. Mappings are devm-managed by callers' device lifetimes.

Dependencies and integration points: It depends on OF address parsing, IO memory accessors, ktime/processor spin waiting, and `common.h` shared-memory operation types. It is used by mailbox, SMC, and OP-TEE static SMT transports.

Risks and edge cases: `shmem_tx_prepare()` gives up after twice the channel timeout but returns void, so transports proceed even after warning that the channel is likely compromised. The 32-bit IO copy path warns on misalignment and count not multiple of 4. Misconfigured shmem size is rejected using `max_msg_size + SCMI_SHMEM_LAYOUT_OVERHEAD`. Poll completion compares tokens to avoid stale completion, but late firmware replies can still stress transport recovery.

Test signals: Device-tree validation should reject missing/non-compatible/undersized shmem. Transport tests should cover interrupt-enabled and polling messages, late response channel-free waiting, 32-bit `reg-io-width`, response status extraction, notification extraction, and channel clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/shmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/system.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/system.c

Purpose: This file implements the SCMI System Power protocol notification decoder. It does not expose normal protocol ops; it registers event support so consumers such as `scmi_power_control.c` can subscribe to platform-originated system power state notifications.

Important APIs/types/functions: `struct scmi_system_info` records graceful timeout support and whether `SYSTEM_POWER_STATE_NOTIFY` exists. `scmi_system_request_notify()` sends notify enable/disable. `scmi_system_set_notify_enabled()` is the notification core hook. `scmi_system_fill_custom_report()` decodes agent ID, flags, state, and optional timeout into `scmi_system_power_state_notifier_report`. `system_protocol_events` describes one source and one event.

Control flow: Protocol init allocates private state, marks graceful timeout support for major version 2 or later, checks whether notify command is supported, and stores private state. The notification core calls support checks, enablement, and report filling when a P2A event arrives. Timeout is accepted only for graceful shutdown when the protocol version supports it.

State and persistence: Runtime private state is devm-managed. There is a fixed `SCMI_SYSTEM_NUM_SOURCES` of 1. No persistent storage is used.

Dependencies and integration points: It depends on `protocols.h`, `notify.h`, SCMI public system power report types, and the SCMI notification framework. It registers as `SCMI_PROTOCOL_SYSTEM` and feeds the system power control driver.

Risks and edge cases: Payload size differs by version because the timeout field is optional. Report filling rejects unexpected sizes and unsupported event IDs. Timeout is zeroed for non-shutdown or non-graceful requests even if payload includes a value. The protocol exposes no ops, only events.

Test signals: Test version 1 vs version 2 payload sizes, notify command absent/present, graceful shutdown timeout parsing, non-shutdown timeout zeroing, invalid payload sizes, and notifier registration by the system power driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Kconfig

Purpose: This Kconfig file defines build-time selection for SCMI transport drivers and helper capability symbols.

Important APIs/types/functions: Internal booleans `ARM_SCMI_HAVE_TRANSPORT`, `ARM_SCMI_HAVE_SHMEM`, and `ARM_SCMI_HAVE_MSG` indicate that at least one transport, shared-memory transport support, or message-buffer transport support is configured. User-visible tristates select mailbox, SMC, OP-TEE, and VirtIO transports. Additional booleans enable SMC atomic mode, VirtIO version 1 compliance, and VirtIO atomic mode.

Control flow: Selecting a transport pulls in the common "have transport" symbol and the relevant shmem/msg helper support. Mailbox and SMC default to `y` when dependencies allow. OP-TEE defaults to `y` with `OPTEE`. VirtIO does not default to enabled. Atomic mode options are conditional on their transports.

State and persistence: This is build configuration only. The selected values persist in the kernel config and determine compiled objects and runtime capabilities.

Dependencies and integration points: It depends on kernel subsystems `MAILBOX`, `HAVE_ARM_SMCCC_DISCOVERY`, `OPTEE`, and `VIRTIO`. It integrates with the SCMI core build so at least one transport exists and the appropriate common helper objects are compiled.

Risks and edge cases: Default-enabled transports can increase footprint unexpectedly. Atomic mode options trade sleeping behavior for busy waiting and should be validated under real timing constraints. VirtIO strict version compliance may reject legacy devices such as older kvmtool backends.

Test signals: Compile matrix should cover each transport as built-in and module where supported, with and without atomic options and VirtIO version compliance. Kconfig tests should confirm symbols select the needed shared memory/message helper support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Makefile

Purpose: This Makefile maps SCMI transport Kconfig symbols to transport module objects and applies a targeted compiler flag workaround for SMC on Thumb2 Clang builds.

Important APIs/types/functions: It builds `scmi_transport_smc.o` from `smc.o`, `scmi_transport_mailbox.o` from `mailbox.o`, `scmi_transport_optee.o` from `optee.o`, and `scmi_transport_virtio.o` from `virtio.o`. It removes `CC_FLAGS_FTRACE` from `smc.o` when `CONFIG_THUMB2_KERNEL=y` and `CONFIG_CC_IS_CLANG=y`.

Control flow: The SMC object is listed before mailbox to give its compatible matching precedence. Object inclusion follows `obj-$(CONFIG_...)`.

State and persistence: Build metadata only; no runtime state.

Dependencies and integration points: It consumes transport Kconfig symbols and produces kernel objects/modules named by the transport Kconfig help text. The ftrace flag removal integrates with ARM SMCCC register constraints.

Risks and edge cases: Matching precedence can affect devices compatible with multiple SCMI transport bindings. The Thumb2/Clang workaround prevents R7 conflicts with SMCCC but also disables ftrace instrumentation for `smc.o` in that configuration.

Test signals: Build all transport combinations, verify module names and object composition, and compile Thumb2 Clang profiling builds to ensure `smc.o` avoids the R7 frame-pointer conflict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/mailbox.c

Purpose: This file implements the SCMI mailbox transport using Linux mailbox channels and shared memory. It supports one bidirectional channel, separate A2P/P2A channels, and optional completion channels depending on device-tree `mboxes`/`shmem` layout.

Important APIs/types/functions: `struct scmi_mailbox` stores mailbox client/channels, SCMI channel info, shmem mapping, channel mutex, and IO ops. `mailbox_chan_validate()` validates and maps mailbox indices. `mailbox_chan_setup()` maps shmem, requests mailbox channels, and initializes state. `mailbox_send_message()` serializes sends through `chan_lock`. `mailbox_mark_txdone()` calls mailbox txdone and unlocks. Fetch/clear/poll helpers delegate to shared memory ops. `scmi_mailbox_desc` advertises timeout, max messages, and max payload.

Control flow: The mailbox core calls `tx_prepare()` before sending to write the SCMI shared memory message. RX callbacks reject spurious A2P IRQs when the channel is not free and otherwise call the SCMI core RX callback with the shared-memory header. Send locks the channel, submits the xfer to the mailbox layer, and leaves the lock held until the SCMI core calls mark_txdone after response processing. Clearing a P2A channel can send an interrupt/doorbell back to firmware if the shmem flags request it.

State and persistence: Per-channel transport state is devm-managed and attached to `cinfo->transport_info`. The mailbox lock prevents mailbox queueing from invalidating SCMI timeouts. There is no persistent storage.

Dependencies and integration points: It depends on the Linux mailbox framework, device tree, shared memory operations, and the SCMI transport driver macro. It matches `arm,scmi`.

Risks and edge cases: Device-tree validation is strict about allowed mailbox/shmem counts but supports several layouts, so binding tests are important. Spurious IRQ detection matters after timeouts. If `mbox_send_message()` fails, the mutex is unlocked immediately; otherwise completion must always reach `mark_txdone()` to avoid deadlock. The descriptor `max_msg` is limited by mailbox queue length.

Test signals: Validate DT layouts with 1 to 4 mailboxes and 1 to 2 shmem entries, TX/RX-only setup, spurious late IRQ tracing, polling completion, P2A notification clear doorbell, mailbox send failure, and timeout behavior with serialized channel locking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/optee.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/optee.c

Purpose: This file implements SCMI over the OP-TEE SCMI PTA. It supports both static SMT shared memory channels and dynamic OP-TEE MSG shared memory buffers, registers an SCMI platform transport after discovering the OP-TEE service, and enforces a single OP-TEE SCMI service instance.

Important APIs/types/functions: `enum scmi_optee_pta_cmd` defines PTA commands for capabilities, SMT processing, MSG processing, and channel acquisition. `struct scmi_optee_channel` stores channel ID, TEE session, caps, rx length, mutex, SCMI cinfo, static shmem or dynamic msg buffer, IO ops, TEE shm, and list node. `struct scmi_optee_agent` stores TEE context and channel list. Key functions include `open_session()`, `get_capabilities()`, `get_channel()`, `setup_dynamic_shmem()`, `setup_static_shmem()`, `scmi_optee_chan_setup()`, `scmi_optee_send_message()`, fetch/clear/mark helpers, and the TEE client probe/remove.

Control flow: The TEE client driver probes the SCMI PTA UUID, opens a TEE context, queries capabilities, publishes `scmi_optee_private`, and registers the SCMI platform transport driver. Channel setup reads `linaro,optee-channel-id`, chooses static shmem if the SCMI node has `shmem` or dynamic TEE shm otherwise, opens a session, tries to convert it to a system session, asks PTA for a channel handle, marks the channel polling-only, and links it. Send locks the channel and either prepares a MSG buffer then invokes `PTA_SCMI_CMD_PROCESS_MSG_CHANNEL`, or prepares SMT shmem then invokes `PTA_SCMI_CMD_PROCESS_SMT_CHANNEL`. Mark txdone unlocks the channel.

State and persistence: Global `scmi_optee_private` stores the single agent. Channel state and sessions are runtime only. Dynamic TEE shared memory is freed during channel free. The agent context is closed after platform driver unregister if no channels remain.

Dependencies and integration points: It depends on OP-TEE TEE client APIs, UUID matching, device tree channel IDs, SCMI shared memory helpers, SCMI message-buffer helpers, and platform transport registration. It matches `linaro,scmi-optee` for SCMI platform nodes and a fixed PTA UUID for service discovery.

Risks and edge cases: Only one OP-TEE SCMI service is allowed. Remove unregisters the platform driver, then returns early if channel list is not empty, leaving context cleanup deferred by design but worth testing. Dynamic MSG mode uses one TEE shm for request and response memrefs. All channels are polling-only (`no_completion_irq`), so timeout settings matter. `scmi_optee_private` publication uses memory barriers; consumers must not race before probe completes.

Test signals: Test PTA absent, capabilities lacking SMT/MSG, static and dynamic channel setup, invalid channel IDs, session open failures, system-session warning path, MSG and SMT send/response paths, channel free list removal, and service remove with active/inactive channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/optee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/smc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/smc.c

Purpose: This file implements SCMI over ARM SMCCC SMC/HVC calls with shared memory. It supports standard `arm,scmi-smc`, parameterized shmem address passing, Qualcomm capability ID calls, optional completion IRQ, and optional atomic mode.

Important APIs/types/functions: `struct scmi_smc` stores optional IRQ, cinfo, shmem mapping, IO ops, mutex or atomic in-flight token, SMCCC function ID, optional shmem page/offset parameters, and optional capability ID. `smc_chan_setup()` maps shmem, reads `arm,smc-id`, handles Qualcomm cap ID and `arm,scmi-smc-param`, requests named `a2p` IRQ if present, and initializes locking. `smc_send_message()` prepares shmem and invokes SMCCC. `smc_msg_done_isr()` calls core RX callback. `smc_mark_txdone()` releases the channel.

Control flow: Only TX channels are supported. Send acquires either mutex or atomic busy-wait in-flight lock, writes shared memory, rings SMCCC with cap ID or page/offset parameters, and leaves the lock held until txdone. If the SMCCC return value is nonzero, the lock is released and `-EOPNOTSUPP` is returned. If no IRQ is configured, `cinfo->no_completion_irq` tells the core completion happens without interrupt. Descriptor marks sync commands completed on SMCCC return.

State and persistence: Per-channel runtime state is devm-managed and attached to `cinfo`. Atomic mode stores the active sequence token in an atomic; non-atomic mode uses a mutex. No persistent data exists.

Dependencies and integration points: It depends on ARM SMCCC, OF IRQ/address helpers, shared-memory helpers, SCMI transport registration, and optional `CONFIG_ARM_SCMI_TRANSPORT_SMC_ATOMIC_ENABLE`. It matches `arm,scmi-smc`, `arm,scmi-smc-param`, and `qcom,scmi-smc`.

Risks and edge cases: Atomic mode busy-waits until the in-flight token clears. The shmem page/offset scheme limits shmem addressability to 44 bits. Qualcomm capability ID is read from the last 8 bytes of shmem. Missing IRQ changes completion assumptions. Lock release depends on `mark_txdone()` after response fetch.

Test signals: Test all compatibles, SMCCC unsupported return, IRQ and polling/no-IRQ modes, atomic and mutex locking, parameterized shmem address values, Qualcomm cap ID extraction, timeout recovery, and module unload/free IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/smc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/virtio.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/virtio.c

Purpose: This file implements SCMI over VirtIO. It uses a command virtqueue for A2P traffic and an optional event virtqueue for P2A notifications, with explicit handling for polling races, timed-out replies, channel lifetime, and buffer ownership.

Important APIs/types/functions: `struct scmi_vio_channel` stores a virtqueue, cinfo, free and pending lists, deferred TX worker, RX flag, max messages, spinlocks, shutdown completion, and refcount. `struct scmi_vio_msg` stores request/input message buffers, rx length, max length, polling index/status, poll lock, and refcount. Core transport ops are `virtio_chan_available()`, `virtio_chan_setup()`, `virtio_chan_free()`, `virtio_send_message()`, fetch response/notification, `virtio_mark_txdone()`, and `virtio_poll_done()`. Virtio driver entry points are `scmi_vio_probe()`, `scmi_vio_remove()`, and `scmi_vio_validate()`.

Control flow: Virtio probe enforces one device, discovers TX and optional RX vqs, initializes channels, caps max messages at token capacity, stores `scmi_vdev`, readies the device, and registers the SCMI platform transport. Channel setup creates the deferred worker for TX, allocates message buffers sized to max SCMI PDU, feeds RX buffers or returns TX buffers to the free list, then marks the channel ready. Send acquires the channel, gets a free message, prepares SCMI MSG payload, binds polled messages to `xfer->priv`, submits scatterlists, and kicks the virtqueue. Completion callback disables callbacks, drains used buffers, calls core RX callback, and finalizes buffers. Polling uses virtqueue used-index polling, dequeues until the target message is found, places unrelated prefetched messages on a pending list, and schedules the deferred worker. Mark txdone frees only messages safe to release and leaves timed-out owned buffers for later host return.

State and persistence: State is in the single virtio device, per-channel refcounts, free/pending lists, message refcounts, and polling status. No state persists across device removal. `virtio_break_device()` and cleanup completions coordinate shutdown with concurrent RX paths.

Dependencies and integration points: It depends on VirtIO core, `virtio_scmi.h`, SCMI message-buffer operations, platform transport registration, and optional config for VirtIO version 1 compliance and atomic mode. It matches `VIRTIO_ID_SCMI` and platform compatible `arm,scmi-virtio`.

Risks and edge cases: Polling can dequeue unrelated replies, so pending list and deferred worker correctness are critical. Timed-out buffers must not be reused until returned by the device; otherwise host-owned buffers could be corrupted. Single-device global `scmi_vdev` requires careful memory barriers. Channel cleanup must coordinate with callback loops. Version 1 compliance can reject legacy devices.

Test signals: Test TX-only and TX+RX feature negotiation, virtqueue size caps, no-free-message `-EBUSY`, IRQ completions, polling completions, concurrent poll/IRQ races, timed-out late replies, prefetched pending processing, remove while callbacks are active, legacy VirtIO validation behavior, and notification fetch on RX queue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Kconfig

Purpose: This Kconfig file defines NXP i.MX vendor SCMI protocol extension drivers for BBM, CPU, LMM, and MISC protocols.

Important APIs/types/functions: `IMX_SCMI_BBM_EXT` enables RTC/button BBM support. `IMX_SCMI_CPU_EXT` enables i.MX CPU protocol operations and depends on `IMX_SCMI_CPU_DRV`. `IMX_SCMI_LMM_EXT` enables Logical Machine Manager operations and depends on `IMX_SCMI_LMM_DRV`. `IMX_SCMI_MISC_EXT` enables miscellaneous controls and depends on `IMX_SCMI_MISC_DRV`. All depend on `ARM_SCMI_PROTOCOL` or compile-test with OF and default to `y` on `ARCH_MXC`.

Control flow: Config selections determine whether corresponding vendor protocol modules are built from the Makefile. The dependencies on external i.MX consumer drivers prevent protocol extensions from being built unless consumers are available, except BBM.

State and persistence: Build configuration only.

Dependencies and integration points: Integrates NXP vendor protocol implementations with the SCMI framework and i.MX architecture defaults. The module names are `imx-sm-bbm`, `imx-sm-cpu`, `imx-sm-lmm`, and `imx-sm-misc`.

Risks and edge cases: Default `y` on `ARCH_MXC` can compile vendor protocol code into kernels with matching architecture. Compile-test coverage depends on OF. Consumer-driver dependency symbols must remain synchronized with public `linux/scmi_imx_protocol.h` users.

Test signals: Build i.MX configs with each extension built-in/module/disabled, compile-test non-i.MX OF builds, and verify modules register vendor SCMI protocol aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Makefile

Purpose: This Makefile maps NXP i.MX SCMI vendor protocol Kconfig symbols to their module objects.

Important APIs/types/functions: It builds `imx-sm-bbm.o`, `imx-sm-cpu.o`, `imx-sm-lmm.o`, and `imx-sm-misc.o` based on `CONFIG_IMX_SCMI_BBM_EXT`, `CONFIG_IMX_SCMI_CPU_EXT`, `CONFIG_IMX_SCMI_LMM_EXT`, and `CONFIG_IMX_SCMI_MISC_EXT`.

Control flow: Standard `obj-$(CONFIG_...)` inclusion controls which protocol extension objects are linked.

State and persistence: Build metadata only.

Dependencies and integration points: It pairs with the i.MX vendor Kconfig and module aliases in each C file.

Risks and edge cases: Object names must match the module names described in Kconfig and the source files. No ordering constraints are expressed.

Test signals: Build each extension as built-in and module and verify expected objects/modules are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-bbm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-bbm.c

Purpose: This file implements the NXP i.MX SCMI BBM vendor protocol for RTC time/alarm, button state, GPR counts, and RTC/button notifications.

Important APIs/types/functions: `struct scmi_imx_bbm_info` caches RTC and GPR counts. Protocol ops include `rtc_time_get`, `rtc_time_set`, `rtc_alarm_set`, and `button_get`. Notification helpers map `SCMI_EVENT_IMX_BBM_RTC` and `SCMI_EVENT_IMX_BBM_BUTTON` to `IMX_BBM_RTC_NOTIFY` and `IMX_BBM_BUTTON_NOTIFY`, and `scmi_imx_bbm_fill_custom_report()` decodes flags into `scmi_imx_bbm_notif_report`.

Control flow: Init logs protocol version, reads protocol attributes for RTC/GPR counts, and stores private state. RTC set/get/alarm validate `rtc_id` against `nr_rtc`, build command payloads with 64-bit seconds split low/high, and send xfers. Button get reads a 32-bit state. Notification enablement sends RTC notification flags for update/rollover/alarm or a button enable flag. Report filling distinguishes RTC vs button events and sets source ID.

State and persistence: Runtime private state stores counts only. RTC time/alarm state is persisted by platform firmware/hardware, not by the driver. Notification subscription is runtime firmware/core state.

Dependencies and integration points: It depends on SCMI core protocol handles, notification framework, public `linux/scmi_imx_protocol.h`, and i.MX vendor IDs. It registers with `module_scmi_protocol()` using `SCMI_PROTOCOL_IMX_BBM`, vendor, and subvendor.

Risks and edge cases: Notification `src_id` is ignored for RTC enablement and always sends RTC ID 0, which may be intentional but limits multi-RTC handling. RTC report sets `*src_id` to `rtc_evt` rather than RTC ID, which affects notification source routing. Attribute parsing assumes firmware returns valid counts. RTC time units are seconds.

Test signals: Test RTC count validation, get/set/alarm enable/disable, button state, notification enable/disable for RTC/button, report decoding for all RTC flags, multi-RTC firmware behavior, and module alias matching by vendor protocol ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-bbm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-cpu.c

Purpose: This file implements the NXP i.MX SCMI CPU vendor protocol for CPU start/stop, reset vector programming, and started-state query.

Important APIs/types/functions: `struct scmi_imx_cpu_info` stores CPU count. Ops are `cpu_reset_vector_set`, `cpu_start`, and `cpu_started`. `scmi_imx_cpu_protocol_attributes_get()` reads CPU count. `scmi_imx_cpu_attributes_get()` reads and logs each CPU name. `scmi_imx_cpu_validate_cpuid()` bounds-checks CPU IDs.

Control flow: Init reads protocol attributes, logs the number of CPUs, then loops over each CPU and reads attributes. Start/stop validates the CPU ID and chooses `SCMI_IMX_CPU_START` or `SCMI_IMX_CPU_STOP`. Reset-vector set validates CPU ID, builds flags for start/boot/resume, splits the 64-bit vector, and sends the command. Started query reads CPU info and treats run modes START and SLEEP as started.

State and persistence: Runtime private state stores the CPU count. Reset vectors and CPU run modes live in platform firmware/hardware. No persistent kernel storage is used.

Dependencies and integration points: It depends on SCMI protocol handle ops, public i.MX SCMI protocol types, and vendor protocol registration. It is meant for i.MX CPU management consumers.

Risks and edge cases: `SCMI_IMX_CPU_INFO_GET` xfer is initialized with rx size 0 while the code reads `t->rx.buf`, which relies on core max-rx behavior or may be a bug; this deserves targeted testing. Init fails if reading any CPU attributes fails, making partial firmware discovery fatal. Flag assembly mixes `cpu_to_le32(0)` with ORed `le32_encode_bits()` values, which is acceptable only if endian helpers produce compatible types.

Test signals: Test CPU count parsing, CPU attribute read loop, start/stop invalid and valid IDs, reset-vector flags combinations, started query for all run modes, and response sizing for `SCMI_IMX_CPU_INFO_GET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-lmm.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-lmm.c

Purpose: This file implements the NXP i.MX SCMI Logical Machine Manager vendor protocol for logical machine information, boot/power-on, reset vector setup, and shutdown.

Important APIs/types/functions: `struct scmi_imx_lmm_priv` stores logical-machine count. Ops are `lmm_power_boot`, `lmm_info`, `lmm_reset_vector_set`, and `lmm_shutdown`. `scmi_imx_lmm_protocol_attributes_get()` reads and caps the number of logical machines at `SCMI_IMX_LMM_NR_MAX`. `scmi_imx_lmm_attributes()` reads per-LM state, error status, and name.

Control flow: Init reads the protocol version and LM count, rejects counts above 16, and stores private state. `lmm_power_boot()` validates LM ID and chooses boot or power-on command. `lmm_shutdown()` validates LM ID and sends a graceful flag only when requested. `lmm_reset_vector_set()` builds LM ID, CPU ID, reserved flags as zero, and 64-bit reset vector before sending. Attribute reads are on demand through the ops table.

State and persistence: The driver caches only LM count. LM state, error status, and reset vectors are controlled by firmware/hardware. No persistent kernel storage exists.

Dependencies and integration points: It depends on SCMI core xfer ops, public i.MX protocol definitions, and vendor protocol registration with `SCMI_PROTOCOL_IMX_LMM`.

Risks and edge cases: `scmi_imx_lmm_reset_vector_set()` does not validate `lmid` even though other operations do; invalid LM IDs may be passed to firmware. The `flags` argument to reset-vector set is ignored and transmitted as zero. Attribute xfer uses rx size 0 while reading a response structure, similar to the CPU file and worth validating. Count validation protects only against above-max values, not zero behavior.

Test signals: Test LM count limits, boot vs power-on, graceful and non-graceful shutdown, invalid LM IDs for every op including reset-vector set, attribute response sizing, and reset vector low/high encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-lmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-misc.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-misc.c

Purpose: This file implements the NXP i.MX SCMI MISC vendor protocol for device/board controls, notifications, build/board/config info discovery, and syslog retrieval.

Important APIs/types/functions: `struct scmi_imx_misc_info` stores device control count, board control count, and reason count. Ops are `misc_ctrl_set`, `misc_ctrl_get`, `misc_ctrl_req_notify`, and `misc_syslog`. Event support decodes `SCMI_EVENT_IMX_MISC_CONTROL`. Helper commands discover build info, board info, config info, and paginated syslog data.

Control flow: Init reads protocol attributes, then best-effort queries build info, board info, and config info, ignoring `-EOPNOTSUPP` but failing on other errors. Control validation separates device controls below `BRD_CTRL_START_ID` from board controls above it. `misc_ctrl_get()` bounds returned value count against max SCMI message size and rx length before copying. `misc_ctrl_set()` bounds the requested value count and sends a variable-length payload. Notification enablement is unusual: enable returns success without sending, while disable sends flags 0; active request notification is exposed through `misc_ctrl_req_notify`. Syslog retrieval uses the generic iterator with returned/remaining counts.

State and persistence: Private state caches control/reason counts. Control values, syslog, build, board, and config information live in firmware. Notification state is runtime firmware/core state.

Dependencies and integration points: It depends on SCMI core, notification framework, iterator helpers, `get_max_msg_size()`, public i.MX protocol types, and vendor registration with `SCMI_PROTOCOL_IMX_MISC`.

Risks and edge cases: `scmi_imx_misc_ctrl_validate_id()` uses `ctrl_id > mi->nr_dev_ctrl`; if IDs are zero-based, `ctrl_id == nr_dev_ctrl` may be incorrectly allowed. Board control lower-bound logic accepts IDs from `nr_dev_ctrl + 1` up to `BRD_CTRL_START_ID - 1` because the first condition only checks `ctrl_id < BRD_CTRL_START_ID && ctrl_id > nr_dev_ctrl`, so boundary semantics need confirmation. `misc_ctrl_get()` rejects `*num >= max_num`, which may reject exactly full-capacity replies. Syslog iterator writes into caller-provided array sized by initial `*size`; firmware returning more than requested depends on iterator max-resource enforcement.

Test signals: Test control ID boundaries, get/set variable lengths at max message size, notification request/disable behavior, event report payload sizes, build/board/config optional unsupported paths, syslog pagination, and malformed returned/remaining counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/voltage.c -->
# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/voltage.c

Purpose: This file implements the SCMI Voltage protocol agent. It discovers voltage domains and supported levels, exposes config get/set and level get/set operations, and supports asynchronous voltage level changes when firmware advertises them.

Important APIs/types/functions: `struct voltage_info` stores domain count and the domain array. `struct scmi_voltage_info` is populated for consumers with domain ID, name, levels, segmented flag, negative-voltage allowance, and async-level-set support. Iterator helpers `iter_volt_levels_prepare_message()`, `iter_volt_levels_update_state()`, and `iter_volt_levels_process_response()` parse `VOLTAGE_DESCRIBE_LEVELS`. Protocol ops are `num_domains_get`, `info_get`, `config_set`, `config_get`, `level_set`, and `level_get`.

Control flow: Init reads protocol attributes to get domain count, allocates domain descriptors, and loops over domains. For each domain it sends `VOLTAGE_DOMAIN_ATTRIBUTES`, stores name and flags, optionally fetches extended name, notes async support, then retrieves voltage levels through the iterator. Level descriptors can be a list or segmented triplet; invalid descriptors cause the domain to have zero levels. Config set masks config to low 4 bits. Level set uses synchronous xfer unless the domain supports async and mode is `SCMI_VOLTAGE_LEVEL_SET_AUTO`, in which case it waits for a delayed response and validates the returned domain ID.

State and persistence: Domain metadata and level arrays are devm-managed runtime state. Actual voltage configuration and level are firmware/hardware state. No persistent kernel storage is used.

Dependencies and integration points: It depends on SCMI core xfer and iterator helpers, public voltage protocol types, extended-name helper, and protocol registration as `SCMI_PROTOCOL_VOLTAGE`. Regulator or power clients consume `scmi_voltage_proto_ops`.

Risks and edge cases: Segmented descriptors must return exactly three entries in one response; otherwise the domain is invalidated. Negative voltage values are accepted and flagged. Per-domain attribute xfer errors are skipped with rx reset, so domains can remain default/invalid without failing whole init. `__scmi_voltage_get_u32()` requests rx size 0 but reads `t->rx.buf`, which relies on core behavior and merits testing. Async completion validates domain ID but only logs voltage level.

Test signals: Test no domains, listed vs segmented levels, invalid descriptor counts, extended names, negative values, config mask behavior, sync and async level set, delayed response wrong domain ID, invalid domain IDs, and level get/config get response sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/voltage.c -->
