<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dlm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dlm.h

## Purpose
Declares the Distributed Lock Manager tracepoint ABI. It covers local lock/unlock API entry and completion, AST/BAST callbacks, recovery communication (`rcom`) traffic, DLM protocol messages, userspace plock messages, and low-level send/receive return codes.

## APIs, Control Flow, and State
Important events are `dlm_lock_start/end`, `dlm_unlock_start/end`, `dlm_bast`, `dlm_ast`, `dlm_send_rcom`, `dlm_recv_rcom`, `dlm_send_message`, `dlm_recv_message`, `dlm_plock_read`, `dlm_plock_write`, `dlm_send`, and `dlm_recv`. Formatter macros decode lock flags (`DLM_LKF_*`), modes (`NL`, `CR`, `CW`, `PR`, `PW`, `EX`), status-block flags, lock-block flags, header commands, message versions, message types, and rcom types. The message tracepoints convert little-endian wire fields with `le*_to_cpu()` before storing them. Dynamic arrays carry resource names, message extras, and recovery payloads. The only state held by the header is event payload schema; live lockspace, lock block, and resource state remains in `fs/dlm`.

## Dependencies, Integration, Risks, and Tests
Depends on DLM public constants, `uapi/linux/dlm_plock.h`, tracepoint APIs, and the private `fs/dlm/dlm_internal.h`, making it tightly coupled to on-wire and in-memory DLM structures. Integration spans cluster lock acquisition, conversion, cancellation, unlock, recovery membership exchange, plock coordination, and transport send/receive paths. Risks are ABI drift between struct fields and trace formatting, excessive payload copying for resource names or variable message sections, kernel-lock error normalization in `dlm_lock_end`, and tracepoints reading partially initialized message data. Test signals include `dlm_tool`/cluster lock traffic with tracing enabled, recovery scenarios that emit rcoms, plock tests, endian-sensitive protocol checks, and compile coverage when DLM internals change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dlm.h -->
