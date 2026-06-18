# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_csa.h

Purpose: this header exposes the static CSA manager contract for device, VM, and firmware command paths that need the reserved context-save area.

Important APIs/types: `AMDGPU_CSA_SIZE` defines the default static CSA size as 128 KiB. Public declarations include `amdgpu_get_total_csa_size()`, `amdgpu_csa_vaddr()`, allocation/free helpers, and VM map/unmap helpers.

Control flow and integration: device init code allocates the static CSA object, per-file VM setup maps it through `amdgpu_map_static_csa()`, command-generation code computes offsets from `amdgpu_csa_vaddr()`, and teardown unmaps/frees it. The header is included by paths that do not need implementation details of `amdgpu_csa.c`.

State and persistence: no state is stored in the header. The APIs manipulate per-device BO state and per-VM VA mappings in memory.

Dependencies: declarations require amdgpu core types such as `struct amdgpu_device`, `struct amdgpu_bo`, `struct amdgpu_vm`, and `struct amdgpu_bo_va`.

Risks: the searched amdgpu tree shows `amdgpu_get_total_csa_size()` declared here but no definition or call in this subset, which may be a stale declaration or defined outside the visible tree in other configurations. Consumers must keep size and address assumptions synchronized with firmware expectations. Any change to `AMDGPU_CSA_SIZE` can affect reserved VA layout and preemption packet construction.

Test signals: compile/link coverage for all declared APIs, SR-IOV preemption coverage, and static analysis for unused or undefined declarations are the key signals for this header.
