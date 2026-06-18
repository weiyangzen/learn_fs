## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sync.h

Purpose: declares AMDGPU sync modes, the sync object container, and public fence collection/manipulation APIs.

Important APIs and types: `enum amdgpu_sync_mode` defines ALWAYS, not-equal-owner, equal-owner, and EXPLICIT filtering modes. `struct amdgpu_sync` is a 16-bucket hash table of fence entries. Function prototypes cover creation, direct fence add, reservation/KFD extraction, peek/get, clone/move, push-to-job, wait, free, and subsystem init/fini.

Control flow: the header defines the external lifecycle: initialize a sync object, collect fences, optionally inspect or move dependencies, push them to jobs or wait, and free resources.

State and persistence: sync state is in-memory fence references only; no persistent state.

Dependencies and integration points: depends on Linux hashtable and forward-declared DMA/AMDGPU types. It integrates with command submission, VM updates, BO reservation handling, scheduler jobs, and KFD.

Risks: callers must call `amdgpu_sync_create()` before use and `amdgpu_sync_free()` after use. The object is not self-locking. Small hash size is intentional but can be a performance concern with many fence contexts.

Test signals: command submission dependency tests, reservation sync tests, clone/move/free leak checks, and scheduler dependency integration.
