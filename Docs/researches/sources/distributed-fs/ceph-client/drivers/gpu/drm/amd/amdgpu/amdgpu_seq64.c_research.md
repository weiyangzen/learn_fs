## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_seq64.c

Purpose: implements a global pool of 64-bit GPU/CPU-visible slots mapped into reserved VM address space. It is used for user queue fence memory, TLB counters, and VM updates.

Important APIs and functions: `amdgpu_seq64_init()` allocates a GTT BO of `AMDGPU_VA_RESERVED_SEQ64_SIZE`, zeros it, and initializes the bitmap. `amdgpu_seq64_fini()` frees it. `amdgpu_seq64_alloc()` finds a free slot, sets the bitmap, and returns VM VA, optional GPU address, and CPU pointer. `amdgpu_seq64_free()` clears a slot by VA. `amdgpu_seq64_map()` locks the VM page directory and BO using `drm_exec`, adds the BO to a VM, maps it at the reserved seq64 VA range as readable/uncached, and updates page tables. `amdgpu_seq64_unmap()` locks and removes a file-private mapping.

Control flow: VA base is computed with `AMDGPU_VA_RESERVED_SEQ64_START(adev)` and sign-extended. Mapping uses `drm_exec_until_all_locked()` with retry-on-contention around VM PD and BO locks, then `amdgpu_vm_bo_add`, `amdgpu_vm_bo_map`, and `amdgpu_vm_bo_update`; failures delete the BO VA before cleanup. Allocation is first-fit over `adev->seq64.used`, with no visible lock in this file, so callers must provide serialization or accept bitmap atomicity assumptions.

State and persistence: `adev->seq64` stores the backing BO, GPU address, CPU base pointer, slot count, and bitmap. Per-file mappings are stored in `fpriv->seq64_va`. State is runtime-only but GPU-visible while mapped.

Dependencies and integration points: depends on AMDGPU BO and VM APIs, reserved VA constants, GMC sign extension, and DRM exec locking. It is initialized/finalized from device lifecycle and used by user queue fence code.

Risks: allocation/free bitmap operations are not locked here, so concurrent callers could race unless higher-level code serializes. `amdgpu_seq64_free()` trusts VA arithmetic; invalid VA below base underflows before division. Mapping failure paths clean up BO VA but leave caller-owned `*bo_va` pointer stale unless caller discards it. The doc comment in the header says `free` takes GPU address, while implementation expects VA.

Test signals: device init/fini, concurrent user queue fence allocation/free, VM map/unmap per file, reserved VA correctness across GPU address modes, and ENOSPC behavior after exhausting slots.
