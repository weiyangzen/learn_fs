
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
