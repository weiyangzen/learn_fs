
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_gem.c

## Purpose
Implements Nouveau GEM object lifetime, mmap fault handling, legacy GEM creation/info/CPU sync ioctls, legacy ABI16 pushbuf validation/relocation/submission, and per-client VMA open/close handling.

## Important APIs, Types, and Functions
Externally used functions include `nouveau_gem_new()`, `nouveau_gem_object_del()`, `nouveau_gem_object_open()`, `nouveau_gem_object_close()`, `nouveau_gem_ioctl_new()`, `nouveau_gem_ioctl_pushbuf()`, `nouveau_gem_ioctl_cpu_prep()`, `nouveau_gem_ioctl_cpu_fini()`, and `nouveau_gem_ioctl_info()`. Internal validation helpers include `validate_init()`, `validate_list()`, `validate_fini()`, `nouveau_gem_pushbuf_validate()`, and `nouveau_gem_pushbuf_reloc_apply()`. `nouveau_ttm_fault()` customizes TTM mmap faults.

## Control Flow
GEM creation disables UVMM if it has not been initialized, allocates a Nouveau BO, initializes the embedded GEM object, initializes TTM backing, applies valid-domain restrictions on Tesla+, creates a handle, and reports GEM info. Object open creates per-client VMAs for legacy VMM users; UVMM users bind explicitly and no eager VMA is created. Object close drops the VMA reference and either deletes it immediately or queues deletion after the VMA fence signals.

Legacy pushbuf ioctl rejects UVMM clients, finds an ABI16 channel, checks limits, copies push/BO/reloc arrays, validates every push buffer is in the BO list, reserves BOs with ww-acquire deadlock handling, chooses placement domains, validates/moves BOs, syncs against reservation fences, applies relocations if presumed offsets changed, emits push calls through GPFIFO/CALL/JUMP paths depending on hardware class, creates a Nouveau fence, optionally waits synchronously, attaches fences to BOs/VMAs, returns updated presumed offsets and next suffix values, and releases all reservations/references.

## State and Persistence
Persistent state lives in `struct nouveau_bo` and GEM object fields: valid domains, no-share flag, per-client VMA list, TTM resource, reservation object, tile/kind/compression metadata, relocation kmap state, and fence pointers on VMAs. Pushbuf validation uses transient `struct validate_op` state and per-BO indices while reserved.

## Dependencies and Integration Points
The file integrates DRM GEM, TTM BO/resource/mmap helpers, dma-resv, Nouveau BO/VMM/fence/channel/ABI16 helpers, NVIF GPFIFO push interfaces, and PRIME hooks through the GEM object function table.

## Risks and Test Signals
Risks are high in userspace ABI validation, reservation deadlock retry, relocation bounds, VMA lifetime after GPU use, UVMM versus legacy UAPI separation, and CPU/GPU synchronization. Test signals include legacy Mesa pushbuf workloads, invalid handles/counts/reloc offsets, no-share export/open denial, mmap page faults, CPU_PREP nowait/write behavior, BO eviction during validation, GPFIFO and pre-NV50 submission paths, and lockdep on reservation locks.
