# sources/distributed-fs/ceph-client/drivers/iommu/intel/cache.c

## Purpose

`intel/cache.c` manages Intel VT-d cache invalidation targets for domains. It tracks per-domain cache tags for IOTLB, device TLB, nested IOTLB, and nested device TLB associations, batches queued-invalidation descriptors by IOMMU unit, and provides range/full/non-present flush helpers for mapping changes.

## Important APIs, Types, and Functions

- `cache_tag_assign` / `cache_tag_unassign`: reference-counted cache-tag list management.
- `cache_tag_assign_domain` / `cache_tag_unassign_domain`: attach/detach cache tags for a domain, device, PASID, and nested parent domain.
- `domain_qi_batch_alloc`: lazy allocation of per-domain invalidation batch storage.
- `domain_get_id_for_dev`: resolves DID, with SVA using `FLPT_DEFAULT_DID`.
- `calculate_psi_aligned_address`: computes page-selective invalidation address/mask covering a range.
- Batch helpers: `qi_batch_flush_descs`, `qi_batch_add_iotlb`, `qi_batch_add_dev_iotlb`, `qi_batch_add_piotlb*`, `qi_batch_add_pasid_dev_iotlb`.
- Flush APIs: `cache_tag_flush_range`, `cache_tag_flush_all`, and `cache_tag_flush_range_np`.

## Control Flow

Assigning a domain lazily allocates `domain->qi_batch`, adds an IOTLB tag, and adds a device-TLB tag when ATS is enabled. Nested domains also assign cache tags to the stage-2 parent. Flush range computes a PSI-aligned address/mask, walks cache tags grouped by IOMMU, flushes queued descriptors when switching IOMMU units, emits IOTLB or device-TLB invalidations by tag type, and flushes the final batch. Non-present flushes either flush write buffers or IOTLBs depending on caching-mode and first-stage paging rules.

## State and Persistence Behavior

Each `dmar_domain` owns a `cache_tags` list protected by `cache_lock` and a reusable `qi_batch`. Tags are reference-counted with `users` so duplicate associations share invalidation targets. Tags persist until unassigned on detach. Batches are transient and reset after submission.

## Dependencies and Integration Points

The file depends on Intel IOMMU internals (`struct dmar_domain`, `struct intel_iommu`, `device_domain_info`), PASID helpers, queued invalidation descriptor builders, ATS metadata, tracepoints, and generic IOMMU dirty/map/unmap paths that call flush helpers.

## Risks and Edge Cases

- `cache_tage_match` appears misspelled but consistently used.
- Device-TLB invalidations are skipped when translation is disabled, per VT-d recommendation.
- Nested device-TLB flushes widen to full-device invalidation because affected nested translations cannot be precisely identified.
- `calculate_psi_aligned_address` must cover unaligned ranges without under-flushing; mask math is subtle.
- `cache_tag_assign` insertion groups tags by IOMMU for batching; list ordering bugs could reduce batching or mix descriptors.

## Test Signals

Test tag reference counting, ATS vs non-ATS devices, nested domain parent assignment rollback, SVA DID selection, PSI alignment for unaligned and full ranges, batching across multiple IOMMUs, queued-invalidation fallback paths, translation-disabled device-TLB skips, `dtlb_extra_inval`, and non-present flush behavior under caching mode and first-stage paging.
