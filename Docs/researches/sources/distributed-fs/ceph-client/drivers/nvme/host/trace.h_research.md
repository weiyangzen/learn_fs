<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h

## Purpose
Declares the NVMe host tracepoint events and connects their print formatting to helper functions in `trace.c`. It captures command submission, request completion, asynchronous events, and submission queue head/tail movement.

## Important APIs, Types, And Functions
Trace events are `nvme_setup_cmd`, `nvme_complete_rq`, `nvme_async_event`, and `nvme_sq`. Helper declarations include `nvme_trace_parse_admin_cmd()`, `nvme_trace_parse_nvm_cmd()`, `nvme_trace_parse_fabrics_cmd()`, and `nvme_trace_disk_name()`. Macros `parse_nvme_cmd()` and `__print_disk_name()` route trace printing based on queue id and opcode. `__assign_disk_name()` copies `gendisk` names into fixed trace entries.

## Control Flow
At command setup, the tracepoint snapshots controller id, queue id, opcode, flags, command id, namespace id, metadata presence, fabrics type, disk name, and cdw10-cdw15 bytes. Completion snapshots result, retries, flags, and status from `nvme_request`. AEN traces capture the result class. SQ traces record queue head and tail. `trace/define_trace.h` materializes the events when included by the trace translation unit.

## State And Persistence
Trace entries are transient ring-buffer records. The header defines the shape of that trace ABI, including fixed field names and string formatting, but does not persist controller state.

## Dependencies And Integration Points
Integrates with Linux tracepoints, block requests, `struct nvme_request`, `struct nvme_command`, `struct nvme_ctrl`, and generated opcode name helpers. It must be included with the correct `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so kernel trace generation can find it.

## Risks
Trace ABI changes can break user-space scripts that parse event fields. The print path must not dereference invalid request or disk data; it snapshots disk names during fast assignment. The parser dispatch assumes queue id zero is admin and nonzero is NVM unless the opcode is fabrics.

## Test Signals
Build with tracing enabled, check generated trace events under tracing events, enable each event, and submit admin, I/O, fabrics, and AEN paths. Validate disk-name handling for namespace and admin requests and confirm `nvme_sq` remains exportable to transport modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/trace.h -->
