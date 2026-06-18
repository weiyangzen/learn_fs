# subset-b-005967 grouped research

This grouped report covers the exact source files assigned to `subset-b-005967`. Each file section is bounded by the reconciliation markers required for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rxrpc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/rxrpc.h

## Purpose
Defines the AF_RXRPC tracepoint catalog. The header gives ftrace, perf, BPF, and tracefs users a typed view of RxRPC local endpoint, peer, bundle, connection, call, skb, packet, ACK, retransmission, congestion-control, path-MTU, RACK/TLP, timer, abort, and RxGK rekey activity.

## Important APIs, Types, and Functions
The file is almost entirely trace metadata: large `EM`/`E_` enum tables, byte-sized enum declarations, `TRACE_DEFINE_ENUM()` exports, and `TRACE_EVENT()` declarations. Important enum tables include `rxrpc_abort_reasons`, `rxrpc_local_traces`, `rxrpc_peer_traces`, `rxrpc_bundle_traces`, `rxrpc_conn_traces`, `rxrpc_client_traces`, `rxrpc_call_traces`, `rxrpc_txqueue_traces`, `rxrpc_txdata_traces`, `rxrpc_receive_traces`, `rxrpc_recvmsg_traces`, `rxrpc_rtt_*_traces`, `rxrpc_timer_traces`, `rxrpc_propose_ack_*`, `rxrpc_ca_states`, `rxrpc_congest_changes`, packet and ACK-name tables, SACK, completion, request-ACK, txbuf, workqueue, PMTUD, RACK, and TLP tables. Major events include `rxrpc_local`, `rxrpc_peer`, `rxrpc_bundle`, `rxrpc_conn`, `rxrpc_client`, `rxrpc_call`, `rxrpc_skb`, `rxrpc_rx_packet`, `rxrpc_tx_packet`, `rxrpc_rx_ack`, `rxrpc_tx_ack`, `rxrpc_recvmsg`, `rxrpc_rtt_tx`, `rxrpc_rtt_rx`, `rxrpc_timer_*`, `rxrpc_congest`, `rxrpc_apply_acks`, `rxrpc_resend`, `rxrpc_rotate`, `rxrpc_req_ack`, `rxrpc_sack`, `rxrpc_pmtud_*`, `rxrpc_rack*`, `rxrpc_tlp_*`, and `rxrpc_rxgk_rekey`.

## Control Flow
RxRPC implementation code calls generated `trace_rxrpc_*()` helpers at lifecycle transitions and packet-processing points. Tracepoint control flow follows the protocol: endpoints and peers are referenced, client bundles and connections are allocated or reused, calls are attached, packets enter through receive paths, ACKs and DATA packets drive send-window rotation, RTT/congestion state is updated, timers are set or expire, retransmission and RACK/TLP logic marks losses, and abort/completion paths terminate calls. The header itself has no executable protocol logic, but each `TP_fast_assign` snapshots the relevant protocol fields before the formatted record reaches trace buffers.

## State and Persistence
No RxRPC protocol state is persisted by this header. State lives in the caller's RxRPC objects, socket buffers, timers, congestion structures, and security state; trace records persist only in tracing ring buffers. The enum/string mappings are compile-time trace ABI metadata and must stay consistent with values used by call sites. Dynamic fields copy packet, SACK, timing, serial, sequence, tx-window, and error information into trace records so later readers do not depend on object lifetime.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `linux/errqueue.h`, RxRPC internal types at call sites, and the kernel trace-event generator via `trace/define_trace.h`. Integrates with `net/rxrpc`, AFS over RxRPC, rxperf, RxKAD/RxGK security handling, UDP socket error reporting, congestion control, RACK/TLP loss recovery, PMTU discovery, and userspace trace tooling that consumes `events/rxrpc/*`.

## Risks
The biggest risk is trace ABI drift: renaming enum labels, changing event fields, or reordering values can break tooling that decodes RxRPC behavior. Tracepoints also dereference live protocol objects, so call sites must pass valid objects and copy variable-length data safely. Very hot packet paths can incur overhead when enabled, especially for verbose ACK, SACK, RTT, and retransmission events. The large enum tables are easy to update incompletely when adding new RxRPC states or reasons.

## Test Signals
Useful signals include building with `CREATE_TRACE_POINTS`, enabling each `events/rxrpc/*` tracepoint under AFS/rxperf traffic, packet loss and reordering tests that exercise retransmission/RACK/TLP, PMTU reduction tests, abort/security failure tests, trace-cmd/perf/BPF field decoding, and lockdep/KASAN runs while tracing hot receive and send paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/rxrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sched.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sched.h

## Purpose
Defines the scheduler tracepoint interface for task lifecycle, wakeups, context switches, migration, kthread work, scheduler statistics, priority inheritance, NUMA balancing, capacity/utilization hooks, and deadline-server debug hooks.

## Important APIs, Types, and Functions
Public events include `sched_kthread_stop`, `sched_kthread_stop_ret`, `sched_kthread_work_queue_work`, `sched_kthread_work_execute_start`, `sched_kthread_work_execute_end`, wakeup events from `sched_wakeup_template`, `sched_switch`, `sched_migrate_task`, `sched_process_free`, `sched_process_exit`, `sched_wait_task`, `sched_process_wait`, `sched_process_fork`, `sched_process_exec`, `sched_prepare_exec`, schedstat events, `sched_pi_setprio`, optional `sched_process_hang`, optional NUMA events, and `sched_wake_idle_without_ipi`. It also declares non-tracefs `DECLARE_TRACE` hooks for PELT, capacity, overutilization, util-est, energy computation, scheduler entry/exit, state changes, need-resched, and deadline throttle/replenish/server transitions. `__trace_sched_switch_state()` maps task state into printable switch state when `CREATE_TRACE_POINTS` is active.

## Control Flow
Scheduler code emits these events at precise scheduling transitions: wakeup starts in the waking context, wakeup completion records the runnable task, `sched_switch` snapshots previous and next task state during context switch, migration records source and destination CPUs, process events follow fork/exec/exit/free/wait paths, and schedstat events are emitted during accounting updates. NUMA balancing events are conditional on `CONFIG_NUMA_BALANCING`; schedstat event definitions compile to no-op variants when `CONFIG_SCHEDSTATS` is disabled.

## State and Persistence
The header persists no scheduler state. Trace records snapshot task command names, pids, priorities, CPU ids, run states, delays, runtime, NUMA ids, nodemasks, exec filenames, and work item pointers into trace buffers. The non-tracefs `DECLARE_TRACE` hooks expose transient scheduler internals to in-kernel instrumentation without creating normal tracefs events.

## Dependencies and Integration Points
Depends on `linux/kthread.h`, `linux/sched/numa_balancing.h`, `linux/binfmts.h`, `linux/tracepoint.h`, scheduler task/runqueue types, cpuset/NUMA helpers, and build-time scheduler configs. Integrates with perf sched, ftrace, eBPF sched tracing, latency profilers, Android/vendor scheduler diagnostics, NUMA balancing analysis, and kernel selftests.

## Risks
Scheduler tracepoints are hot and ABI-sensitive. Changing fields or formats can break tooling. Call sites must avoid expensive work while tracing hot paths, and pointer fields such as work functions or scheduler entities must not be interpreted after object lifetime. Some comments note incomplete deadline handling for priority fields. Conditional events can make tooling config-dependent.

## Test Signals
Signals include `perf sched`, trace-cmd context-switch traces, fork/exec/exit stress tests, kthread worker tests, `CONFIG_SCHEDSTATS` enabled/disabled builds, NUMA balancing workloads, hung-task detection, BPF program attachment to sched tracepoints, and latency regressions when high-frequency events are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sched_ext.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sched_ext.h

## Purpose
Provides tracepoints for the `sched_ext` extensible scheduler framework, mainly for dumping textual state, recording named scheduler-extension events, and observing bypass load-balancing decisions.

## Important APIs, Types, and Functions
Defines `sched_ext_dump`, `sched_ext_event`, and `sched_ext_bypass_lb`. `sched_ext_dump` stores a single string line, `sched_ext_event` stores a string name plus signed delta, and `sched_ext_bypass_lb` records node, CPU count, task count, number balanced, and min/max distribution before and after bypass balancing.

## Control Flow
The sched_ext core or BPF-backed scheduler code emits these tracepoints when producing diagnostic dump lines, accounting named events, or bypassing normal load-balance behavior. Each event copies scalar or string values into the trace record immediately.

## State and Persistence
No state is owned here. Trace buffers persist the copied strings and counters. The events reflect transient scheduler-extension diagnostics and balancing outcomes rather than stable kernel state.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and the sched_ext implementation. Integrates with tracefs/perf/BPF tooling used to debug BPF schedulers, load-balance bypass behavior, and scheduler-extension dumps.

## Risks
String-based event names and dump lines are flexible but weaker ABI than structured fields. High-volume dump/event emission can distort scheduler behavior when enabled. Consumers must treat deltas and balancing counters as point-in-time diagnostics.

## Test Signals
Signals include sched_ext selftests, loading sample BPF schedulers, enabling `events/sched_ext/*`, forcing load imbalance, verifying dump line capture, and checking that tracing does not destabilize scheduler-extension workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sched_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/scmi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/scmi.h

## Purpose
Defines tracepoints for ARM SCMI message transport, fast-channel calls, transfer lifecycle, response waits, receive completion, and payload dumps.

## Important APIs, Types, and Functions
Events are `scmi_fc_call`, `scmi_xfer_begin`, `scmi_xfer_response_wait`, `scmi_xfer_end`, `scmi_rx_done`, and `scmi_msg_dump`. `TRACE_SCMI_MAX_TAG_LEN` bounds copied dump tags. Fields cover protocol id, message id, resource id, values, transfer id, sequence, polling mode, timeout, inflight count, status, channel id, message type, and dynamic payload bytes.

## Control Flow
SCMI drivers emit `scmi_fc_call` for fast-channel accesses, `scmi_xfer_begin` when a message transfer starts, `scmi_xfer_response_wait` while waiting, `scmi_rx_done` when an inbound response/notification arrives, `scmi_xfer_end` on completion, and `scmi_msg_dump` when raw payload logging is requested.

## State and Persistence
The header owns no SCMI state. Trace records snapshot transfer identifiers and optionally copy payload bytes into a dynamic trace array. The copied payload persists only in trace buffers and can outlive transport buffers safely.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, SCMI core transfer state, and transport channel implementations. Integrates with SCMI protocol drivers for clocks, power, sensors, performance, reset, and vendor protocols.

## Risks
Payload dumping can expose firmware data and add overhead. Tags are truncated to six bytes, so consumers should not depend on full labels. Protocol/message ids are numeric and require SCMI protocol context to interpret. Incorrect payload length passed by call sites would affect copied trace data.

## Test Signals
Signals include SCMI selftests, firmware-backed boot traces, timeout/error injection, polling versus interrupt transports, payload dump validation, and checking trace output while exercising clock/performance/sensor protocols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/scmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/scsi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/scsi.h

## Purpose
Defines SCSI mid-layer tracepoints for command dispatch, dispatch errors, command completion, timeouts, and error-handler wakeups, with rich symbolic decoding of opcodes, host bytes, status bytes, protection operations, and queue return codes.

## Important APIs, Types, and Functions
Helper macros include `show_opcode_name`, `show_hostbyte_name`, `show_statusbyte_name`, `show_prot_op_name`, `show_rtn_name`, and `__parse_cdb()`. It declares `scsi_trace_parse_cdb()`. Events include `scsi_dispatch_cmd_start`, `scsi_dispatch_cmd_error`, the `scsi_cmd_done_timeout_template` class, `scsi_dispatch_cmd_done`, `scsi_dispatch_cmd_timeout`, and `scsi_eh_wakeup`.

## Control Flow
The SCSI mid-layer emits start traces when commands are dispatched to low-level drivers, error traces when queueing returns busy/retry codes, done traces when commands complete, timeout traces when timeout handling begins, and EH wakeup traces when the error-handling thread is notified. Dynamic CDB arrays are copied for decode and raw display.

## State and Persistence
No SCSI state is persisted by the header. Trace records snapshot host/channel/id/lun, opcode, CDB bytes, tags, scatter-gather counts, protection operation, result, retries, allowed attempts, and timeout. Records persist in trace buffers after `struct scsi_cmnd` changes or is freed.

## Dependencies and Integration Points
Depends on `scsi/scsi_cmnd.h`, `scsi/scsi_host.h`, `linux/tracepoint.h`, and `linux/trace_seq.h`. Integrates with the block layer request tags, SCSI hosts, low-level drivers, error handling, and storage latency/debug tooling.

## Risks
Opcode tables must be kept current as SCSI commands evolve. Dynamic CDB copying must match `cmd_len`. Trace format is consumed by storage tools, so field changes are risky. Hot command paths can be high volume, and raw CDB logging can expose device command details.

## Test Signals
Signals include SCSI command tracing during fio workloads, queue-depth saturation to trigger dispatch errors, timeout/error-handler injection, protection information tests, command parser coverage for 6/10/12/16/variable CDBs, and trace-cmd/perf decoding checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sctp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sctp.h

## Purpose
Defines SCTP tracepoints for path probing and congestion/window probing so network diagnostics can observe association path state and transport-level flow-control values.

## Important APIs, Types, and Functions
Events are `sctp_probe_path` and `sctp_probe`. `sctp_probe_path` records association pointer, transport pointer, source/destination socket addresses, state, path MTU, cwnd, ssthresh, partial bytes acknowledged, flight size, error count, and heartbeat interval. `sctp_probe` records association pointer, transport pointer, mark, rwnd, unacknowledged count, and flight size.

## Control Flow
SCTP code emits these tracepoints around path monitoring and congestion/window updates. The event assignment copies address structures and transport counters from live association/transport state into tracing records.

## State and Persistence
The header owns no state. Trace records persist snapshots of SCTP association and transport counters, address pairs, and flow-control metrics in the tracing ring buffer.

## Dependencies and Integration Points
Depends on SCTP socket/transport structures at call sites and `linux/tracepoint.h`. Integrates with the SCTP stack, networking trace tools, congestion diagnostics, and heartbeat/path-failover investigations.

## Risks
Address formatting and transport pointer values are diagnostic, not stable identifiers. High-frequency SCTP traffic can generate large trace volume. Consumers must handle both IPv4 and IPv6 socket address payloads correctly.

## Test Signals
Signals include SCTP association setup, multihoming failover, heartbeat timeout tests, cwnd/rwnd changes under load, packet loss injection, and trace output validation for IPv4/IPv6 paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/signal.h -->
# sources/distributed-fs/ceph-client/include/trace/events/signal.h

## Purpose
Defines signal-generation and signal-delivery tracepoints used to diagnose process signaling, blocked/ignored signals, signal queueing, and delivery handler behavior.

## Important APIs, Types, and Functions
`TP_STORE_SIGINFO()` normalizes `siginfo_t` values into errno, code, and optional sending pid/uid. The local enum maps trace outcomes such as delivered, ignored, already pending, overflow fail, loss, and wakeup. Events are `signal_generate` and `signal_deliver`.

## Control Flow
Signal code emits `signal_generate` when a signal is generated or queued for a target task, including destination pid, signal number, group flag, result, and siginfo fields. It emits `signal_deliver` when a signal is delivered to userspace with handler pointer and blocked-mask metadata.

## State and Persistence
No signal state is stored here. Trace records copy comm names, pids, signal numbers, siginfo summary, handler pointer, blocked mask, and result code. The records remain available after task signal structures move on.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, task and signal structures, `siginfo_t`, and signal mask helpers. Integrates with process lifecycle debugging, ptrace/seccomp/audit-adjacent diagnostics, and userspace trace consumers.

## Risks
Signal tracing can expose process ids, command names, handlers, and signal metadata. Result semantics are tightly coupled to signal core behavior; adding new outcomes requires updating symbolic mappings. Handler pointers are diagnostic and can be affected by address randomization.

## Test Signals
Signals include kill/tkill/tgkill tests, real-time signal queue overflow, ignored and blocked signals, handler delivery, group signals, ptrace/seccomp interactions, and BPF/ftrace attachment to `events/signal/*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/siox.h -->
# sources/distributed-fs/ceph-client/include/trace/events/siox.h

## Purpose
Defines tracepoints for SIOX bus data transfer, exposing set-data and get-data operations with device name, data length, and payload bytes.

## Important APIs, Types, and Functions
Events are `siox_set_data` and `siox_get_data`. Both take a `struct siox_device *`, a byte buffer, and a length. Each record stores `dev_name(&sdevice->dev)`, length, and a dynamic byte array rendered as hex.

## Control Flow
SIOX bus/controller code emits the events when writing data to or reading data from a SIOX device. The tracepoint copies the data buffer into a dynamic trace array during `TP_fast_assign`.

## State and Persistence
No bus state is owned by the header. Trace records persist device names and payload snapshots in trace buffers, independent of the original buffer lifetime.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and `struct siox_device` from the SIOX subsystem. Integrates with SIOX bus drivers and device diagnostics.

## Risks
Payload tracing can expose device data and can be expensive for larger transfers. The tracepoint trusts the provided length and buffer pointer. Device names are strings, not stable hardware ids.

## Test Signals
Signals include SIOX read/write operations with tracing enabled, zero-length and maximum-length buffer coverage, device unbind while tracing, and trace hex output comparison against expected bus transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/siox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/skb.h -->
# sources/distributed-fs/ceph-client/include/trace/events/skb.h

## Purpose
Defines socket-buffer lifecycle tracepoints for packet drops, skb consumption, and datagram copy faults, with symbolic drop-reason decoding.

## Important APIs, Types, and Functions
The header expands `DEFINE_DROP_REASON()` into `TRACE_DEFINE_ENUM()` exports and symbolic drop strings. Events are `kfree_skb`, `consume_skb`, and `skb_copy_datagram_iovec`. `kfree_skb` records skb pointer, drop location, protocol, and `enum skb_drop_reason`; `consume_skb` records skb and location; `skb_copy_datagram_iovec` records skb pointer, length, and error.

## Control Flow
Networking code emits `kfree_skb` when an skb is dropped with a reason, `consume_skb` when it is successfully consumed, and `skb_copy_datagram_iovec` when copying packet data to userspace iovecs completes or fails.

## State and Persistence
The header stores no skb state. Trace records snapshot pointers, protocol, reason, locations, lengths, and errors into tracing buffers. Pointer values are lifetime-limited diagnostics and must not be dereferenced by consumers.

## Dependencies and Integration Points
Depends on `linux/skbuff.h`, `linux/netdevice.h`, `linux/tracepoint.h`, and drop-reason definitions. Integrates with core networking, drop monitor tooling, perf/BPF packet-drop analysis, and protocol stacks.

## Risks
Drop-reason enum/string drift can break tooling. Hot packet paths can generate large trace volume. Pointer/location fields can expose kernel addresses depending on formatting restrictions. Consumers must handle `NOT_SPECIFIED` and evolving drop reasons.

## Test Signals
Signals include packet drop tests across protocol layers, drop_monitor/BPF consumers, skb consume tracing under normal traffic, datagram copy fault injection, and build checks when drop reasons are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/skb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/smbus.h -->
# sources/distributed-fs/ceph-client/include/trace/events/smbus.h

## Purpose
Defines SMBus tracepoints for controller operations, reads, replies, and final results, including SMBus protocol type and transfer payloads.

## Important APIs, Types, and Functions
Events are `smbus_write`, `smbus_read`, `smbus_reply`, and `smbus_result`. The first three are `TRACE_EVENT_CONDITION` events that suppress unsupported protocol encodings. Fields cover adapter number/name, address, flags, read/write direction, command, protocol, length, and data bytes. Helper formatting maps SMBus protocol constants to names and prints values conditionally by transfer type.

## Control Flow
I2C/SMBus core code emits write/read request traces before operations, reply traces after read data is available, and result traces with return status. Conditional tracepoints prevent malformed protocol categories from being logged through the detailed format path.

## State and Persistence
No adapter or transfer state is persisted by the header. Trace records copy adapter identity, command metadata, payload bytes, and result codes into trace buffers.

## Dependencies and Integration Points
Depends on I2C/SMBus constants and `linux/tracepoint.h`. Integrates with the I2C core, SMBus host controller drivers, client drivers, and bus-debug tooling.

## Risks
SMBus payloads may contain device configuration or sensor data. Protocol-specific length handling must stay aligned with SMBus core semantics. Conditional filtering means some invalid inputs produce no detailed event, which tooling must account for.

## Test Signals
Signals include SMBus byte/word/block transfers, read/write result traces, invalid protocol tests, adapter-name formatting, PEC/flag coverage, and bus fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/smbus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sock.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sock.h

## Purpose
Defines socket tracepoints for receive-queue pressure, socket memory limits, TCP/INET state transitions, socket error reports, data-ready callbacks, and send/receive message lengths.

## Important APIs, Types, and Functions
The header exports TCP state enums and `show_inet_sock_state()`. Events are `sock_rcvqueue_full`, `sock_exceed_buf_limit`, `inet_sock_set_state`, `inet_sk_error_report`, `sk_data_ready`, and the `sock_msg_length` class used by `sock_send_length` and `sock_recv_length`. Fields include socket cookies, protocol/family, ports, v4/v6 addresses, queue allocation/limits, rmem/wmem, old/new states, errors, and message lengths.

## Control Flow
Networking code emits these events when receive queues fill, per-protocol memory pressure exceeds limits, INET sockets change state, errors are reported, data-ready callbacks run, and send/receive operations account message lengths. Address/port fields are captured at the event site.

## State and Persistence
The header owns no socket state. Trace records persist snapshots of socket identifiers, memory accounting, addresses, ports, states, errors, and lengths in trace buffers. Socket cookies give tooling a more stable correlation key than raw pointers.

## Dependencies and Integration Points
Depends on socket, inet, TCP state, and tracepoint helpers. Integrates with core networking, TCP/UDP diagnostics, BPF socket tracing, memory-pressure analysis, and latency/throughput instrumentation.

## Risks
Socket tracepoints can expose address/port metadata and high event volume. State enum mappings must stay current. Call sites must handle IPv4/IPv6 address capture correctly, and consumers should not treat cookies as globally persistent across reboot.

## Test Signals
Signals include TCP connect/close state transitions, UDP/TCP receive queue saturation, memory pressure tests, socket error injection, BPF attachment, IPv4/IPv6 address formatting, and send/receive size accounting checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sof.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sof.h

## Purpose
Defines Sound Open Firmware core tracepoints for widget setup/free, PCM pointer positions, IPC3 period elapsed reports, IPC stream position reception, and IPC4 firmware configuration.

## Important APIs, Types, and Functions
The `sof_widget_template` event class backs `sof_widget_setup` and `sof_widget_free`. Other events are `sof_ipc3_period_elapsed_position`, `sof_pcm_pointer_position`, `sof_stream_position_ipc_rx`, and `sof_ipc4_fw_config`. Fields include widget names, DSP component ids, host/Dai positions, wall-clock values, PCM delay, stream tag, and IPC4 firmware config values.

## Control Flow
SOF core and PCM code emit widget events during topology/widget lifecycle, position events while handling period elapsed or PCM pointer updates, stream-position traces when IPC replies arrive, and config traces when IPC4 firmware configuration is known.

## State and Persistence
The header owns no audio state. Trace records persist copied widget names and scalar position/config snapshots. Position values are time-sensitive diagnostics and must be interpreted relative to PCM stream activity.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SOF audio structures at call sites. Integrates with ALSA SoC SOF topology, IPC3/IPC4 firmware communication, PCM runtime diagnostics, and audio latency debugging.

## Risks
Position traces can be high frequency. Widget names and component ids must match topology lifetimes. IPC version differences mean tools must distinguish IPC3 and IPC4 events. Misinterpreting host/Dai position units can lead to false latency conclusions.

## Test Signals
Signals include SOF topology load/unload, PCM playback/capture under tracing, period elapsed validation, IPC3 and IPC4 firmware boots, XRUN/latency tests, and trace output comparison to ALSA runtime position.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sof.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sof_intel.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sof_intel.h

## Purpose
Defines Intel-specific SOF tracepoints for HDA IRQs, IPC firmware doorbell direction, D0I3C updates, IPC checks, DSP PCM stream binding, stream status, and stream IRQ checks.

## Important APIs, Types, and Functions
Events include `sof_intel_hda_irq`, `sof_intel_ipc_firmware_response`, `sof_intel_ipc_firmware_initiated`, `sof_intel_D0I3C_updated`, `sof_intel_hda_irq_ipc_check`, `sof_intel_hda_dsp_pcm`, `sof_intel_hda_dsp_stream_status`, and `sof_intel_hda_dsp_check_stream_irq`. The IPC firmware template captures header and extension registers; stream events capture stream tags, channel maps, positions, status, and IRQ metadata.

## Control Flow
Intel HDA/SOF driver code emits IRQ traces when interrupts arrive, IPC traces around firmware-originated or host-originated messages, D0I3C traces when power state control changes, and stream traces while mapping or checking DSP streams.

## State and Persistence
No driver state is stored here. Trace records snapshot register values, stream identifiers, channel maps, buffer positions, and status bits into trace buffers. These are diagnostic copies of transient hardware/driver state.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, Intel HDA SOF driver structures, and firmware IPC register definitions. Integrates with ALSA SOF Intel platforms, HDA interrupt handling, power management, IPC debugging, and PCM stream diagnostics.

## Risks
Hardware register semantics vary by platform and firmware generation. High-rate IRQ or stream-status tracing can be noisy. Consumers must interpret status bits with the matching Intel SOF platform documentation.

## Test Signals
Signals include Intel SOF boot, IPC ping/firmware response tracing, suspend/resume with D0I3C updates, PCM playback/capture IRQs, stream status transitions, and comparison against HDA register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sof_intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spi-mem.h -->
# sources/distributed-fs/ceph-client/include/trace/events/spi-mem.h

## Purpose
Defines tracepoints for SPI memory operations, showing operation start/stop, command/address/dummy/data phases, bus widths, DTR flags, data direction, and return status.

## Important APIs, Types, and Functions
Events are `spi_mem_start_op` and `spi_mem_stop_op`. `TRACE_SYSTEM` is `spi-mem` and `TRACE_SYSTEM_VAR` is `spi_mem` for C identifier compatibility. `decode_dtr()` prints DTR phase markers. Fields are extracted from `struct spi_mem_op`, including opcode, address bytes/value, dummy bytes, bus widths, data bytes, direction, and data buffer pointer, plus return code on stop.

## Control Flow
SPI memory core code emits start before executing a memory operation and stop after completion. The tracepoint snapshots the operation descriptor rather than copying the payload buffer.

## State and Persistence
The header owns no SPI memory state. Trace records persist operation descriptors and buffer pointers. Payload contents are not copied, so the buffer pointer is only useful as a correlation hint while the operation is live.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SPI memory operation types. Integrates with SPI NOR/NAND, controller drivers implementing `spi_mem_ops`, and flash transaction debugging.

## Risks
Pointer-only data buffer recording avoids payload overhead but limits postmortem value. DTR, bus-width, and phase semantics must track `struct spi_mem_op` evolution. Trace format uses `spi-mem` naming, so include/trace generation depends on the `TRACE_SYSTEM_VAR` override.

## Test Signals
Signals include SPI NOR reads/writes/erase op traces, DTR-capable flash operations, dummy/address phase validation, controller error injection, and tracefs event format checks for the hyphenated system name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spi-mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/spi.h

## Purpose
Defines core SPI tracepoints for controller idle/busy state, device setup, chip-select changes, message submit/start/done, and transfer start/stop including sampled TX/RX buffers.

## Important APIs, Types, and Functions
Event classes include `spi_controller`, `spi_message`, and `spi_transfer`. Events include `spi_controller_idle`, `spi_controller_busy`, `spi_setup`, `spi_set_cs`, `spi_message_submit`, `spi_message_start`, `spi_message_done`, `spi_transfer_start`, and `spi_transfer_stop`. Helper macros `spi_valid_txbuf()` and `spi_valid_rxbuf()` bound dynamic buffer copying by message optimization flags and transfer length.

## Control Flow
SPI core/controller code emits controller state transitions, setup and chip-select events around device configuration, message events through queue/execute/complete flow, and transfer events around individual transfers. Transfer events copy bounded TX/RX bytes for visibility.

## State and Persistence
No SPI state is persisted here. Trace records copy bus number, chip select, mode, max speed, message/transfer pointers, status, lengths, and optional data bytes. Pointer fields are correlation aids only.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and SPI core structures. Integrates with SPI controller drivers, SPI protocol drivers, spidev diagnostics, and logic-analyzer correlation.

## Risks
Copying transfer buffers can expose device data and add overhead. Optimized or controller-mutated messages may not have valid buffers for copying, hence the helper guards. Chip-select and mode fields must remain aligned with SPI core semantics.

## Test Signals
Signals include SPI message queue tests, setup/mode changes, chip-select toggling, full-duplex transfer tracing, optimized message paths, error status injection, and trace payload comparison to known transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spmi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/spmi.h

## Purpose
Defines SPMI tracepoints for read/write transaction boundaries and command completion, exposing opcode, slave id, address, return status, length, and transferred bytes.

## Important APIs, Types, and Functions
Events are `spmi_write_begin`, `spmi_write_end`, `spmi_read_begin`, `spmi_read_end`, and `spmi_cmd`. Write/read begin events identify opcode, sid, and address; end events add return code and read/write payload where applicable.

## Control Flow
The SPMI core emits begin events before bus transactions and end events after controller completion. `spmi_cmd` covers command-style operations without an address/payload. Dynamic arrays copy transaction data into the trace record.

## State and Persistence
The header owns no SPMI bus state. Trace buffers persist copied transaction metadata and payload bytes. Original buffers may be reused after the event without affecting trace output.

## Dependencies and Integration Points
Depends on `linux/spmi.h` and `linux/tracepoint.h`. Integrates with SPMI controllers, PMIC drivers, regulator/clock/power-management diagnostics, and SoC bring-up tracing.

## Risks
Payload traces can expose PMIC register values. Length and buffer pointer correctness is trusted. High-frequency register polling can generate large trace volume.

## Test Signals
Signals include SPMI register reads/writes, command operations, controller error injection, PMIC driver probe with tracing enabled, and payload hex output verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/spmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sunrpc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sunrpc.h

## Purpose
Defines the comprehensive SunRPC client/server tracepoint catalog used by NFS, lockd, RPCSEC_GSS, RPC transports, rpcbind, server sockets, service pools, caches, and registration paths.

## Important APIs, Types, and Functions
The header exports symbolic decoders for socket types, address families, xprt security policies, client create flags, auth statuses, task flags/runstate, socket states, transport state, service deferral, cache status, and registration operations. Event classes cover XDR buffers, clients, task status/running/queued states, failures, replies, sockets, xprt lifetimes/events, write-lock/congestion, TLS, service XDR messages/buffers, service requests/status, service transports, pools, deferred requests, svcsock lifetimes/classes, cache events, and register events. Named events span `rpc_xdr_*`, `rpc_clnt_*`, `rpc_request`, `rpc_task_*`, bad call/verifier events, reply/rpcb errors, `rpc_buf_alloc`, `rpc_call_rpcerror`, latency and XDR overflow/alignment events, `rpc_socket_*`, `xprt_*`, rpcbind port/register operations, TLS events, `svc_*`, `svc_xprt_*`, `svcsock_*`, cache events, and `svc_unregister`.

## Control Flow
Client-side RPC code emits events during client creation, task scheduling, queueing, run actions, sleeps/wakes, buffer allocation, XDR encode/decode, socket connect/error/state changes, transport reservation/transmit/retransmit/ping, congestion and writelock changes, rpcbind lookup/set/register/unregister, and TLS handshakes. Server-side code emits events during request receive/decode/authenticate/process/send, XDR buffer handling, transport create/enqueue/dequeue/accept/close, pool-thread lifecycle, deferred request handling, socket receive/accept/state, cache lookup/update, and service registration/unregistration.

## State and Persistence
This header owns no RPC state. Trace records snapshot task ids, client ids, XIDs, program/procedure names, versions, server names, transport ids, addresses, ports, socket states, XDR buffer layout, queue names, timeouts, latencies, errors, request statuses, service pool data, and cache identifiers. Dynamic strings and arrays are copied into trace records to survive object reuse.

## Dependencies and Integration Points
Depends on SunRPC headers (`sched.h`, `clnt.h`, `svc.h`, `xprtsock.h`, `svc_xprt.h`), TCP state definitions, `linux/net.h`, `trace/misc/sunrpc.h`, `trace/events/net_probe_common.h`, and tracepoint infrastructure. Integrates directly with NFS client/server, rpcbind, RPC transports over TCP/UDP/TLS/RDMA-adjacent code, RPCSEC_GSS, kernel service caches, and user diagnostics through tracefs/perf/BPF.

## Risks
This is a large trace ABI surface; field or symbolic-name changes can break NFS/RPC observability tools. Many events are hot under NFS workloads, so enabling broad tracing can be expensive. Events expose server names, addresses, ports, procedure names, XIDs, and sometimes auth/cache outcomes. Call sites must pass initialized RPC objects because event assignments dereference nested pointers.

## Test Signals
Signals include NFS mount/read/write/unmount traces, server-side nfsd request handling, rpcbind success/failure paths, socket connect/reset/no-space tests, TLS-enabled RPC, retransmission and timeout injection, XDR overflow/alignment tests, service cache operations, BPF attachment to representative events, and trace format stability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sunrpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sunvnet.h -->
# sources/distributed-fs/ceph-client/include/trace/events/sunvnet.h

## Purpose
Defines tracepoints for the Sun virtual network driver, focused on receive walking, stopped-ACK transmission/deferral/pending state, received stopped ACKs, transmit triggers, and skipped triggers.

## Important APIs, Types, and Functions
Events are `vnet_rx_one`, `vnet_tx_send_stopped_ack`, `vnet_tx_defer_stopped_ack`, `vnet_tx_pending_stopped_ack`, `vnet_rx_stopped_ack`, `vnet_tx_trigger`, and `vnet_skip_tx_trigger`. The stopped-ACK variants share `vnet_tx_stopped_ack_template`.

## Control Flow
Sunvnet code emits receive-walk traces with local/remote session ids, ring index, and ACK need; transmit paths emit stopped-ACK and trigger traces as they decide whether to notify peers or skip redundant triggers.

## State and Persistence
No driver state is stored here. Trace records persist session ids, ring indexes, ACK ranges, packet counts, trigger starts, and errors as scalar snapshots.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h` and sunvnet driver call sites. Integrates with SPARC logical-domain virtual networking diagnostics and ring/ACK flow-control debugging.

## Risks
Trace output is driver-specific and assumes local/remote session id semantics. High packet rates can make receive/trigger tracing noisy. The closing comment references `_TRACE_SOCK_H`, a harmless but misleading copy-paste label.

## Test Signals
Signals include virtual network traffic under sunvnet, stopped-ring/ACK scenarios, trigger send failures, skipped trigger cases, and trace correlation with packet counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/sunvnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/swiotlb.h -->
# sources/distributed-fs/ceph-client/include/trace/events/swiotlb.h

## Purpose
Defines the `swiotlb_bounced` tracepoint for observing DMA mappings that require bounce buffering through the software I/O TLB.

## Important APIs, Types, and Functions
`swiotlb_bounced` takes a `struct device *`, device DMA address, and size. It records device name, DMA mask, device address, transfer size, and whether bouncing was forced by `is_swiotlb_force_bounce(dev)`.

## Control Flow
DMA/SWIOTLB mapping code emits the event when a mapping bounces. The tracepoint snapshots device metadata and bounce cause before returning to DMA mapping flow.

## State and Persistence
The header owns no DMA state. Trace records persist copied device name, DMA mask, address, size, and force/normal mode. They do not retain bounce-buffer contents.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, device DMA fields, and SWIOTLB helpers. Integrates with DMA mapping code, IOMMU/SWIOTLB diagnostics, confidential-computing forced-bounce modes, and device-driver performance analysis.

## Risks
Tracing only bounced mappings can hide successful direct mappings, so rates must be interpreted in context. DMA addresses and device names can be sensitive diagnostics. Call sites must pass valid devices with stable names.

## Test Signals
Signals include forced SWIOTLB boot modes, devices with restricted DMA masks, large DMA mappings, confidential VM bounce behavior, and trace correlation with DMA mapping failures or performance drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/swiotlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/syscalls.h -->
# sources/distributed-fs/ceph-client/include/trace/events/syscalls.h

## Purpose
Defines raw syscall entry and exit tracepoints, exposing syscall number, up to six arguments, and return value for architectures that support syscall tracepoints.

## Important APIs, Types, and Functions
`TRACE_SYSTEM` is `raw_syscalls` while `TRACE_INCLUDE_FILE` is `syscalls`. Under `CONFIG_HAVE_SYSCALL_TRACEPOINTS`, `TRACE_EVENT_SYSCALL(sys_enter)` records syscall id and arguments via `syscall_get_arguments()`, and `TRACE_EVENT_SYSCALL(sys_exit)` records syscall id from `syscall_get_nr()` plus return value. Both use `syscall_regfunc` and `syscall_unregfunc` and are marked `TRACE_EVENT_FL_CAP_ANY`.

## Control Flow
Architecture syscall entry code invokes `sys_enter` before dispatching the syscall, and exit code invokes `sys_exit` with the return value. Registration functions allow arch-specific syscall tracepoint enable/disable handling.

## State and Persistence
No syscall state is owned here. Trace records persist numeric syscall ids, argument snapshots, and return values in tracing buffers. Argument interpretation is architecture and syscall-table dependent.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `asm/ptrace.h`, `asm/syscall.h`, current task state, and architecture syscall tracing support. Integrates with strace-like tracing, perf, ftrace, BPF raw tracepoints, seccomp diagnostics, and audit-adjacent investigations.

## Risks
Raw syscall tracing can expose sensitive arguments such as pointers, file descriptors, addresses, and return codes. Field semantics differ across architectures and compat modes. Tools must map syscall ids against the correct table. Events do not decode pointed-to memory.

## Test Signals
Signals include syscall trace selftests, BPF raw tracepoint programs, arch builds with and without `CONFIG_HAVE_SYSCALL_TRACEPOINTS`, compat syscall coverage, and comparing trace output with known syscall workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/target.h -->
# sources/distributed-fs/ceph-client/include/trace/events/target.h

## Purpose
Defines Linux SCSI target-core tracepoints for command sequencer start and command completion, with opcode, task attribute, status, CDB, sense data, LUN, tag, data length, and initiator identity.

## Important APIs, Types, and Functions
Helper macros mirror SCSI opcode/status decoding: `show_opcode_name`, `show_task_attribute_name`, and `show_scsi_status_name`. Events are `target_sequencer_start` and `target_cmd_complete`. Fields are read from `struct se_cmd`, including `orig_fe_lun`, `tag`, `t_task_cdb`, `data_length`, `sam_task_attr`, `scsi_status`, `sense_buffer`, and session initiator name.

## Control Flow
Target core emits `target_sequencer_start` when a SCSI command enters target command sequencing and `target_cmd_complete` when it completes. Completion traces conditionally copy sense data when status is CHECK CONDITION.

## State and Persistence
The header owns no target-core state. Trace records persist copied CDB bytes, initiator string, sense bytes, status, attributes, and identifiers after the `se_cmd` continues or is freed.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `linux/trace_seq.h`, SCSI protocol/task constants, and `target/target_core_base.h`. Integrates with LIO target fabrics such as iSCSI, Fibre Channel, vhost-scsi, and loopback target diagnostics.

## Risks
Tracing can expose initiator names, CDBs, LUNs, tags, and sense data. The event assumes populated session/node ACL pointers. Opcode tables must track SCSI command additions. Sense length calculation must stay consistent with SPC sense layout.

## Test Signals
Signals include target command tracing through common fabrics, CHECK CONDITION sense paths, task attribute variants, READ/WRITE/INQUIRY commands, initiator login/logout around tracing, and comparison with initiator-side SCSI traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/target.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/task.h -->
# sources/distributed-fs/ceph-client/include/trace/events/task.h

## Purpose
Defines task-management tracepoints for new task creation, task rename, and unknown `prctl()` options.

## Important APIs, Types, and Functions
Events are `task_newtask`, `task_rename`, and `task_prctl_unknown`. `task_newtask` records pid, command name, clone flags, and `oom_score_adj`. `task_rename` records pid, old/new command names, and `oom_score_adj`. `task_prctl_unknown` records the option and four argument words.

## Control Flow
Process management code emits `task_newtask` after task creation with clone flags, `task_rename` when a task command name changes, and `task_prctl_unknown` when `prctl()` receives an unsupported option. Tracepoints copy task strings and scalar values immediately.

## State and Persistence
No task state is persisted by the header. Trace records persist command names, pid, clone flags, OOM adjustment, and prctl arguments in trace buffers. The task may exit or rename again after the event.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, task structures, signal OOM adjustment state, and prctl handling. Integrates with process lifecycle diagnostics, container/runtime tracing, fork/exec analysis, and userspace observability tooling.

## Risks
Clone flags and prctl arguments can expose process behavior and raw argument values. `oom_score_adj` is read through `task->signal`, so call sites must use valid task signal state. Tooling should distinguish this file's task events from scheduler process events.

## Test Signals
Signals include fork/clone workloads, `prctl(PR_SET_NAME)` rename tests, unknown prctl option calls, OOM score adjustment changes before fork/rename, and BPF/ftrace consumers of `events/task/*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/task.h -->
