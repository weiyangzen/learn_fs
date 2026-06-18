# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_smi_events.h

## Purpose
Declares the KFD SMI event producer interface used by KFD, SVM, reset, VM fault, and queue management code.

## Important APIs, Types, And Functions
The header forward-declares `struct amdgpu_reset_context` and exports `kfd_smi_event_open` plus event update functions for VM fault, thermal throttling, GPU reset, page fault start/end, migration start/end, queue eviction/restore, delayed restore rescheduling, GPU unmap, and process lifecycle.

## Control Flow
Callers emit events by passing the relevant `kfd_node`, pid, address range, GPU ids, trigger code, timestamp, or reset context. The implementation handles formatting, filtering, queuing, and wakeups.

## State And Persistence
No state is defined in the header. It exposes the stateful implementation in `kfd_smi_events.c`, where clients and FIFOs are held per opened fd.

## Dependencies And Integration Points
Requires KFD core types such as `struct kfd_node`, `struct kfd_process_device`, `pid_t`, `ktime_t`, and AMD reset context definitions from including translation units. The API is consumed by SVM migration/fault code, queue eviction/restore paths, GPU reset paths, and process attach/detach paths.

## Risks
The prototypes are tightly coupled to SMI record formats. Adding fields or changing units in producers must stay synchronized with userspace expectations and the format macros from KFD UAPI headers.

## Test Signals
Compile coverage should catch signature drift. Runtime coverage should verify each declared producer path can be called with masks enabled and produces parseable records in the SMI fd.
