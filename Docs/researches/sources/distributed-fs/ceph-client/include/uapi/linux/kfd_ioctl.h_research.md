# sources/distributed-fs/ceph-client/include/uapi/linux/kfd_ioctl.h

## Purpose
`kfd_ioctl.h` defines the AMD Kernel Fusion Driver compute UAPI for HSA/ROCm queues, memory, events, SVM, SMI events, CRIU checkpoint/restore, XNACK mode, runtime debugging, and process creation.

## Important APIs, Types, and Functions
The ABI version is 1.22. Queue APIs create, update, destroy, mask CUs, inspect wave state, and allocate GWS. Memory APIs set policy, acquire DRM VM, allocate/free/map/unmap GPU memory, import/export dma-bufs, query dma-buf info, and query available memory. Event APIs create/destroy/set/reset/wait events and carry memory, hardware, and signal data. SMI definitions expose event IDs, trigger enums, mask macros, event strings, and anonymous event FDs. CRIU structures describe process info, device buckets, BO buckets, and restore metadata. SVM uses `kfd_ioctl_svm_args` with variable attributes. Debug APIs use `kfd_ioctl_dbg_trap_args` as an operation multiplexer with many operation-specific structures. Ioctl macros run from `AMDKFD_IOC_GET_VERSION` through `AMDKFD_IOC_CREATE_PROCESS`.

## Control Flow
ROCm userspace queries version and apertures, creates GPU queues, allocates or imports memory, maps it to one or more GPU IDs, waits for events, and controls SVM attributes. Debuggers enable runtime/debug sessions, subscribe to exceptions, suspend/resume queues, set watchpoints, query snapshots, and clear events. CRIU flows pause/evict queues, checkpoint BOs and private state, unpause, restore, and resume.

## State and Persistence
State is per process, per GPU, per queue, per memory handle, per event, per SVM range, and per debug session. Handles and queue IDs persist until explicit destruction or process/device teardown. SMI event FDs hold masks and FIFO state. XNACK mode is process-wide and constrained by active queues.

## Dependencies and Integration Points
It includes `<drm/drm.h>` and `<linux/ioctl.h>`. Integration points include AMDGPU DRM render nodes, ROCm runtime, HSA queues, dma-buf, TTM memory migration, SVM/MMU notifiers, GPU reset/RAS events, CRIU, ptrace/debuggers, and sysfs capability headers.

## Risks and Test Signals
ABI risk is very high: many structs contain userspace pointers, variable arrays, bidirectional counters, version-gated fields, and security-sensitive debug controls. Tests should cover ioctl numbering, structure sizes, partial map/unmap `n_success`, memory flag validation, queue lifetime, event wait timeouts, SVM overlap splitting and aggregation, XNACK refusal with active queues, CRIU operation ordering, SMI privilege gating, debug permission/ptrace checks, snapshot entry sizing, and 32/64-bit compatibility.
