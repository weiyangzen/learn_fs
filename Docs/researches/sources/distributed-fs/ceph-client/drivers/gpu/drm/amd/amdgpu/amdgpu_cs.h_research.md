# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.h

Purpose: this header defines the command-submission parser data structures shared by `amdgpu_cs.c` and helpers that need to inspect CS mappings.

Important APIs/types: `AMDGPU_CS_GANG_SIZE` fixes the maximum submission gang to four scheduler entities/jobs. `struct amdgpu_cs_chunk` stores a copied userspace chunk ID, dword length, and kernel data pointer. `struct amdgpu_cs_post_dep` tracks syncobj output state, optional timeline chain, and point. `struct amdgpu_cs_parser` is the central per-ioctl state object: device/file/context, chunks, gang entities/jobs/leader, `drm_exec`, BO list, memory migration counters, user fence BO, post dependencies, and `amdgpu_sync`. The only declared function is `amdgpu_cs_find_mapping()`.

Control flow and integration: `amdgpu_cs.c` fills this structure progressively through parser passes. Ring parsers and patch hooks can use `amdgpu_cs_find_mapping()` to resolve IB virtual addresses back to BO mappings owned by the current CS reservation ticket.

State and persistence: the parser is transient and freed at ioctl completion. It references persistent objects such as contexts, BO lists, BOs, syncobjs, and VM mappings but does not own their lifetime beyond references acquired by the parser.

Dependencies: the header includes `drm_exec`, `ww_mutex`, amdgpu job, BO-list, and ring declarations. It forward-declares `struct amdgpu_bo_va_mapping` to avoid exposing VM internals.

Risks: changing field ownership or cleanup expectations risks leaks, double puts, or lock-order bugs in the ioctl path. Increasing `AMDGPU_CS_GANG_SIZE` would require revisiting userspace ABI expectations, scheduler dependency wiring, and VM invalidation constraints.

Test signals: build and runtime coverage should include ring parse callbacks that include this header, gang-size boundary tests, and failure-path cleanup tests that ensure each parser-owned reference is dropped exactly once.
