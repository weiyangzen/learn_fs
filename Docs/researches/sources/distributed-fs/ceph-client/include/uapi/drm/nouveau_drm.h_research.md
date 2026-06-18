# sources/distributed-fs/ceph-client/include/uapi/drm/nouveau_drm.h

## Purpose

`nouveau_drm.h` defines the Nouveau NVIDIA DRM userspace ABI for getparams, legacy channel/GPU-object operations, GEM allocation and pushbuffer submission, CPU prep/fini, SVM migration, modern VM_INIT/VM_BIND, EXEC submission, and zcull information. The complete 586-line header was read.

## Important APIs, Types, and Functions

Public ioctls include `GETPARAM`, `CHANNEL_ALLOC/FREE`, `SVM_INIT/BIND`, `GEM_NEW/PUSHBUF/CPU_PREP/CPU_FINI/INFO`, `VM_INIT`, `VM_BIND`, `EXEC`, and `GET_ZCULL_INFO`. Core structs include getparam, channel alloc/free, GEM info/new/pushbuf BO/reloc/push, CPU prep/fini, `drm_nouveau_sync`, VM init/bind op/bind, EXEC push/exec, zcull info, and SVM init/bind. Constants define domains, tile flags, push/reloc limits, sparse mapping, async VM bind, and syncobj/timeline types.

## Control Flow

Legacy flow allocates a channel, creates GEM BOs, submits pushbuffers with BO/reloc/push arrays, and synchronizes CPU access. Modern flow calls `VM_INIT` before BOs/channels, maps and unmaps GEM objects or sparse ranges through `VM_BIND`, then executes virtual-address pushes through `EXEC` with wait/signal sync arrays. SVM flow initializes unmanaged VA and issues migration bind commands.

## State and Persistence Behavior

Channels, GEM handles, VM initialization, VA mappings, sparse regions, sync operations, and SVM ranges are client/fd state. `VM_INIT` ordering establishes the VM_BIND mode early. Async VM_BIND work can complete later and signal sync objects. Pushbuf reports available VRAM/GART after submission.

## Dependencies and Integration Points

Depends on `drm.h`. Integrates with Nouveau memory and channel managers, GEM/dma-buf, NVIDIA pushbuffer command streams, DRM syncobj/timeline syncobj, sparse residency, SVM/HMM migration, zcull context state, and Mesa Nouveau/NVK userspace.

## Risks and Edge Cases

Risk areas are deprecated ioctl compatibility, push/reloc/BO limit enforcement, relocation domain validation, `VM_INIT` ordering, sparse unmap semantics, async VM_BIND synchronization, SVM bitfield masking, and stale or overlapping VA mappings before EXEC.

## Test Signals

Cover getparams, channel lifecycle, GEM domains/tile info, pushbuf limits and reloc variants, CPU prep nowait/write, VM_INIT ordering failures, VM_BIND map/unmap/sparse/async sync, EXEC multi-push syncobj/timeline paths, SVM migration bitfields, zcull query, and invalid flag/handle/range cases.
