<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c

## Purpose
`xe_dma_buf.c` implements Xe PRIME dma-buf export/import, attachment policy, mapping, CPU-access migration, and move notifications. It bridges Xe BO/TTM placement rules with the Linux dma-buf and DRM PRIME interfaces.

## Important APIs, types, and functions
Export-side ops include `xe_dma_buf_attach()`, `detach()`, `pin()`, `unpin()`, `map_dma_buf()`, `unmap_dma_buf()`, `begin_cpu_access()`, and `release()` through `xe_dmabuf_ops`. `xe_gem_prime_export()` rejects VM-private, purgeable, or purged BOs, marks them willneed, prepares TTM export, and installs Xe dma-buf ops. Import uses `xe_gem_prime_import()`, `xe_dma_buf_create_obj()`, dynamic attach ops, and `xe_dma_buf_move_notify()`.

## Control flow and integration points
Attachment disables peer-to-peer if PCI P2P distance is invalid, otherwise requires migration to TT memory when not P2P. Pin scans all attachments to decide if VRAM is allowed; if not, it migrates to TT and pins externally. Mapping builds an SG table from TT pages or VRAM manager ranges. Import of a self-exported dma-buf returns the GEM object directly unless KUnit forces different-device behavior; external imports create an SG BO bound to the dma-buf reservation before dynamic attach.

## State and persistence behavior
Runtime PM refs are held per attachment. Exported BOs hold willneed state until dma-buf release. Imported objects store `obj->import_attach`; move notifications evict importer BO mappings. Placement may change between VRAM and TT depending on attachment mix.

## Dependencies, risks, and test signals
Dependencies include dma-buf, PCI P2PDMA, DRM PRIME, TTM TT, Xe BO migration/pinning, VRAM manager SG allocation, validation, and runtime PM. Risks include pinned VRAM with non-P2P importers, SG table lifetime mismatches, CPU access in current placement after migration failure, purgeable export races, and global attachment-list policy. Test signals include PRIME export/import, self-import, P2P and non-P2P attachments, CPU read access, purge/madvise rejection, move-notify eviction, KUnit live dma-buf tests, and runtime PM leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.c -->
