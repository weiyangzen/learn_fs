<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c

## Purpose

`kfd_chardev.c` is the `/dev/kfd` userspace ABI front door. It registers the KFD character device, binds each opened file descriptor to a `struct kfd_process`, dispatches the full `AMDKFD_IOC_*` ioctl table, and implements KFD mmap offsets for doorbells, events, reserved memory, and remapped MMIO.

## Important APIs, Types, and Entry Points

- `kfd_chardev_init()` / `kfd_chardev_exit()` create and remove the character device, class, and `/dev/kfd` node.
- `kfd_open()` rejects 32-bit tasks and creates/references the calling `kfd_process`; `kfd_release()` drops that reference and handles secondary-context notifier release.
- `kfd_ioctl()` is the central ABI dispatcher: it validates ioctl numbers, canonicalizes sizes from `amdkfd_ioctls[]`, copies user data, gates CRIU ioctls on capability, calls validators such as `kfd_ioctl_svm_validate()`, invokes handlers, and copies results back.
- Queue handlers include create/destroy/update, CU mask update, wave-state query, scratch backing VA, trap handler, and GWS allocation. They mostly validate ABI arguments then call PQM/DQM helpers.
- Memory handlers allocate/free/map/unmap GPUVM objects, import/export dma-buf, query dma-buf metadata, acquire DRM VMs, and report available memory.
- CRIU handlers serialize and restore process private data, device mappings, BOs, queues, events, and SVM ranges.
- Debug/runtime handlers enable or disable runtime debug state and forward `AMDKFD_IOC_DBG_TRAP` operations to `kfd_debug.c`.
- `kfd_mmap()` decodes `KFD_MMAP_TYPE_*` offsets and routes to doorbell, event, reserved-memory, or MMIO remap paths.

## Control Flow

Open stores the owning `kfd_process` in `filep->private_data`. Later ioctls require the same process group leader, except capability-gated checkpoint/restore operations may be driven by a ptracing helper. This makes the FD a process-scoped KFD context rather than a freely shareable descriptor.

Queue creation validates user pointers, ring sizes, queue type, priority, and encoded PM4 target XCC, then locks `p->mutex`, binds the requested GPU PDD, allocates process doorbells if needed, acquires queue buffers, calls `pqm_create_queue()`, returns queue ID and doorbell mmap offset, and raises a debugger queue-new event.

GPU memory allocation rejects invalid size and unsupported userptr on secondary processes. With SVM enabled it flushes deferred SVM work and rejects overlapping SVM registrations. It validates large-BAR requirements for public VRAM, handles special doorbell/MMIO offsets, allocates through AMDGPU GPUVM, creates a PDD IDR handle, updates VRAM accounting, and returns a combined KFD handle.

Map/unmap ioctls copy a GPU-ID array, resume at `n_success`, bind peer PDDs, map or unmap the same memory object across devices, sync page-table work, flush KFD TLBs, and remove DMA mappings after unmap flushes. CRIU follows a staged protocol: process-info evicts queues and returns sizes, checkpoint serializes state with BO FD installation last, restore recreates devices/BOs/objects and blocks MMU notifications until resume, unpause restores queues, and resume re-enables SVM/MMU activity for a target PID.

Debug ioctls locate target processes by PID, enforce primary contexts and ptrace ownership, require runtime-enabled state for mutating trap operations, and delegate activation, exception, watchpoint, wave, snapshot, and flag operations to the debugger backend.

## State and Persistence Behavior

Persistent state is mostly outside this file but is mutated here under `p->mutex`: PDDs, queues, doorbells, GPUVM handles, aperture fields, XNACK mode, CRIU paused state, debug runtime fields, and debugger references. Memory handles persist in each PDD's `alloc_idr` and combine GPU ID with IDR handle for userspace. Queue state persists in PQM/DQM, with this file holding ABI validation and buffer acquisition/release glue. CRIU private records persist user GPU IDs, IDR handles, mapped-device lists, queue/event/SVM state, and restored mmap offsets.

## Dependencies and Integration Points

The file integrates with KFD process management, PQM/DQM, events, doorbells, SVM, topology, SMI events, debug support, CRIU helpers, TLB flushing, reserved-memory mapping, and AMDGPU KGD/GPUVM APIs. It depends on `uapi/linux/kfd_ioctl.h`, Linux copy/user access, capability checks, dma-buf, IDRs, ptrace/task references, and VMA remapping.

## Risks and Edge Cases

- Ioctl struct extension relies on zeroing driver-side tails; every handler must still validate user pointer/count pairs.
- SVM overlap checks and GPUVM allocation have delicate lock ordering around `current->mm`, SVM locks, and `p->mutex`.
- Map/unmap restart through `n_success` must remain accurate to avoid double operations or DMA mapping leaks.
- Public VRAM depends on large-BAR detection; wrong classification exposes inaccessible memory or rejects valid allocations.
- CRIU restore preserves old IDR handles and partially allocates objects before final validation, so error cleanup and MMU-notification resume are critical.
- Debug trap ioctls cross process boundaries through PID, ptrace, task/mm references, and process refs.
- `kfd_mmap()` receives user-controlled encoded offsets; every mapper must validate GPU, size, and type.

## Test and Validation Signals

Exercise open/close ownership, ioctl ABI size compatibility, queue lifecycle, GPUVM allocation/map/unmap/import/export, SVM overlap rejection, CRIU staged checkpoint/restore with FD leak injection, debug trap operations, and all mmap offset types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_chardev.c -->
