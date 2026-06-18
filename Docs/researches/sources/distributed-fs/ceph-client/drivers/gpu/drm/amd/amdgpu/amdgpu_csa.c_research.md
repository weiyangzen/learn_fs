# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.c

Purpose: this file manages the static CSA, a reserved GPU virtual address mapping used for command-stream context save/restore and SR-IOV graphics preemption support. It allocates a kernel BO, zeroes it, maps it into per-process VMs at a reserved address, and unmaps it during teardown.

Important APIs and functions: `amdgpu_csa_vaddr()` returns the sign-extended reserved CSA virtual address. `amdgpu_allocate_static_csa()` creates a kernel BO in the requested domain, maps CPU memory, zero-fills it, and stores `adev->virt.csa_cpu_addr`. `amdgpu_free_static_csa()` releases the BO. `amdgpu_map_static_csa()` locks the VM page directory and CSA BO with `drm_exec`, creates a `bo_va`, and maps it readable/writable/executable at the supplied CSA address. `amdgpu_unmap_static_csa()` locks the same objects, unmaps the virtual address, and deletes the VM BO mapping.

Control flow: device initialization allocates the static CSA BO; file/VM initialization maps it for clients that need SR-IOV preemption metadata; file teardown unmaps it. Both map and unmap use `drm_exec_until_all_locked()` with contention retry before touching VM mapping state.

State and persistence: persistent state is in-memory only: the BO pointer, CPU address in `adev->virt.csa_cpu_addr`, and per-VM `amdgpu_bo_va` mapping. There is no on-disk persistence. The mapping is deterministic because it uses the reserved `AMDGPU_VA_RESERVED_CSA_START()` address.

Dependencies and integration: this code depends on amdgpu BO kernel allocation/free helpers, VM BO add/map/unmap/delete helpers, `drm_exec`, GMC sign extension, and SR-IOV/GFX/MES users that consume `amdgpu_csa_vaddr()` for preemption payloads. Call sites include device init, KMS open/close VM setup, MES context mapping, and GFX/SDMA/VPE command paths.

Risks: `amdgpu_allocate_static_csa()` ignores the return value of `amdgpu_bo_create_kernel()` and only checks `*bo`, so unexpected helper behavior could hide errors. Map/unmap must keep VM PD and BO locking order consistent with broader VM code. Executable PTE permissions are intentionally broad and should remain limited to the reserved CSA object. The reserved VA must not collide with user mappings.

Test signals: SR-IOV preemption tests, KMS open/close with CSA map/unmap, VM teardown leak checks, lockdep for VM/BO reservation, allocation failure injection, and GPU preemption tests that verify firmware can read the CSA payload at the expected address.
