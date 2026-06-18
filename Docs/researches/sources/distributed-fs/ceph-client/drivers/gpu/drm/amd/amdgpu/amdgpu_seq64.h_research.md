## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.h

Purpose: declares the seq64 slot-pool structure and public lifecycle, allocation, free, map, and unmap APIs.

Important APIs and types: `AMDGPU_MAX_SEQ64_SLOTS` derives the number of 64-bit slots from reserved VA size. `struct amdgpu_seq64` holds the backing BO, slot count, GPU address, CPU base pointer, and bitmap. Public functions cover init/fini, allocate/free, and VM map/unmap.

Control flow: no implementation, but callers are expected to initialize the pool once per device, map it into process VMs as needed, allocate 64-bit slots, and free by VA.

State and persistence: runtime state only; backing memory is a GTT BO visible to GPU and CPU.

Dependencies and integration points: includes `amdgpu_vm.h`; used by core device lifecycle and user queue fence/VM update code.

Risks: prototype `amdgpu_seq64_free(struct amdgpu_device *adev, u64 gpu_addr)` names the argument `gpu_addr`, while implementation interprets it as VA. That naming mismatch can mislead callers and reviewers.

Test signals: compile coverage, seq64 user queue fence tests, slot exhaustion/reuse, and VM mapping lifecycle tests.
