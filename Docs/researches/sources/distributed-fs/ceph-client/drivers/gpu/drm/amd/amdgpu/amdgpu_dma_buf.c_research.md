# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_dma_buf.c

## Purpose

`amdgpu_dma_buf.c` implements AMDGPU PRIME/DMA-BUF export and import support. It lets AMDGPU GEM buffer objects be shared with other devices, controls placement and pinning for peer-to-peer and CPU access, maps backing memory into scatter/gather tables, handles dynamic attachment invalidation, and detects XGMI-accessible peer GPU memory.

The file is a bridge between DRM GEM/PRIME, Linux DMA-BUF, TTM memory placement, AMDGPU VM invalidation, PCI P2PDMA policy, and XGMI multi-GPU sharing.

## Important APIs, types, and functions

- `amdgpu_dmabuf_ops` is the exported `dma_buf_ops` table: attach, pin, unpin, map/unmap, release, begin CPU access, mmap, vmap, and vunmap.
- `amdgpu_gem_prime_export()` prepares a GEM BO for export with TTM, rejects userptr and always-valid VM BOs, delegates to `drm_gem_prime_export()`, and installs AMDGPU DMA-BUF ops.
- `amdgpu_gem_prime_import()` returns a same-device exported GEM object directly or creates an imported SG BO and dynamically attaches to the source DMA-BUF.
- `amdgpu_dma_buf_attach()` updates peer-to-peer eligibility, disables P2P for GFX12+ DCC VRAM surfaces and unreachable PCI P2P paths, then updates shared VM BO state under the BO reservation lock.
- `amdgpu_dma_buf_pin()` chooses a pin domain from allowed domains and attachment peer2peer capabilities, preferring VRAM only when all attachments support P2P and move notifiers are available.
- `amdgpu_dma_buf_map()` validates/moves unpinned BOs into GTT or VRAM as appropriate, then builds an `sg_table` for TT pages, VRAM resources, or MMIO-remap resources.
- `amdgpu_dma_buf_unmap()` frees the corresponding SG table through the TT, VRAM, or MMIO-remap path.
- `amdgpu_dma_buf_begin_cpu_access()` moves readable buffers to GTT when supported, improving CPU access performance and avoiding direct VRAM reads.
- `amdgpu_dma_buf_vmap()` and `amdgpu_dma_buf_vunmap()` pin around generic GEM DMA-BUF vmap/vunmap.
- `amdgpu_dma_buf_move_notify()` invalidates mappings for imported buffers and clears/updates VM page tables for VMs referencing the imported BO.
- `amdgpu_dmabuf_is_xgmi_accessible()` detects whether a BO can be accessed by the importing AMDGPU device over XGMI.

## Control flow

Export starts when DRM PRIME calls `amdgpu_gem_prime_export()`. The function rejects BOs that should not be exported, asks TTM to set up export constraints without allowing resource eviction, then returns a DMA-BUF using AMDGPU-specific operations.

Attachment starts through `amdgpu_dma_buf_attach()`. The importer may be another AMDGPU attachment using `amdgpu_dma_buf_attach_ops`; if so, the helper recovers its `amdgpu_device`. The attach callback adjusts `attach->peer2peer` based on compression, XGMI accessibility, and PCI P2P distance, then updates shared VM state.

Map flow first moves an unpinned BO into a device-accessible placement: GTT by default, plus VRAM when the buffer prefers VRAM and the attachment supports P2P. It then returns DMA addresses. TT memory maps normal pages through DMA API, VRAM uses AMDGPU VRAM manager SG allocation, and MMIO-remap uses its dedicated allocator. Unmap chooses the matching free path by resource type and SG page presence.

Import flow returns the original GEM object for same-device AMDGPU DMA-BUFs. For other devices it creates a `ttm_bo_type_sg` BO backed by the DMA-BUF reservation object, restricts placement to GTT, dynamically attaches with AMDGPU attach ops, increments the DMA-BUF refcount, and stores the attachment in `obj->import_attach`.

Move notification invalidates the imported BO in AMDGPU VM lists, evicts it to a null/empty placement if it has a resource, and walks VM BO bases to clear freed mappings and handle moved mappings while carefully dealing with reservation locking conflicts.

## State and persistence behavior

The code mutates BO placement, pin count, flags such as `AMDGPU_GEM_CREATE_CPU_ACCESS_REQUIRED`, `allowed_domains`, `preferred_domains`, import attachments, DMA-BUF `peer2peer` flags, VM BO invalidation state, and page tables for VMs referencing imported BOs. Imported BOs share the exporter DMA-BUF reservation object, so synchronization state persists across drivers.

Mapped SG tables are transient per attachment mapping and must be released via `unmap_dma_buf`. VM invalidation state persists until the next VM update clears or rebuilds page tables. XGMI accessibility marks are consumed by VM mapping code outside this file.

## Dependencies and integration points

The file depends on Linux DMA-BUF, DRM PRIME/GEM helpers, DMA fence reservation objects, TTM, AMDGPU BO/GEM/TTM/VM/XGMI/display helpers, PCI P2PDMA, and DMA mapping APIs. It integrates with `amdgpu_ttm.c` imported SG handling, `amdgpu_vm.c` XGMI and moved-BO handling, display scanout domain policy, and external devices such as RDMA NICs or other GPUs.

## Risks and edge cases

- Peer-to-peer policy is hardware-sensitive. Allowing P2P for GFX12 DCC-compressed VRAM or unreachable PCI topology can corrupt data or fail DMA.
- Pinning chooses VRAM only if every attachment remains peer2peer-capable; a single incompatible attachment forces GTT and affects performance.
- Map/unmap must pair allocation paths exactly. Misidentifying TT vs VRAM vs MMIO-remap SG tables can leak or unmap through the wrong API.
- Move notification has complex locking around VM reservations. If locks cannot be taken it may skip a VM update, relying on later synchronization; errors other than `-EBUSY` are logged.
- Same-device import intentionally returns the existing GEM object rather than wrapping the DMA-BUF file, changing refcount behavior compared with cross-device import.
- Export rejects userptr and `VM_ALWAYS_VALID` BOs; callers must handle `-EPERM`.
- CPU read access migration to GTT is skipped for write-only access or when GTT scanout/access domains are unsupported.

## Test signals

Relevant validation includes DRM PRIME import/export tests, cross-GPU and same-GPU DMA-BUF sharing, RDMA P2P scenarios, GFX12 DCC sharing fallback, XGMI hive P2P mapping tests, repeated map/unmap leak checks, CPU-access readback tests, VM invalidation after exporter movement, and display tests using imported DMA-BUFs under both GTT-supported and VRAM-only scanout policy.
