# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_heap_config.h

Purpose: This header defines the Rogue device virtual address heap map used by application memory contexts and firmware/kernel-only allocations. It is a layout contract for userspace-visible heaps and global execution base programming.

Important APIs/types/functions: Exports heap base/size constants: `ROGUE_GENERAL_HEAP_BASE/SIZE` at 512-640 GiB, `ROGUE_PDSCODEDATA_HEAP_BASE/SIZE` at 872-876 GiB, `ROGUE_RGNHDR_HEAP_BASE/SIZE` at top of a 16 GiB range for BRN63142, `ROGUE_USCCODE_HEAP_BASE/SIZE` at 896-900 GiB, `ROGUE_FW_HEAP_BASE` in the reserved firmware region, `ROGUE_TRANSFER_FRAG_HEAP_BASE/SIZE`, and `ROGUE_VISTEST_HEAP_BASE/SIZE`. There are no functions or structs.

Control flow: None. Allocation code selects heaps based on buffer purpose and uses these ranges to configure GPU virtual memory and global PDS/USC execution bases.

State and persistence behavior: The header has no state, but heap base choices persist as ABI-visible virtual addresses in memory contexts. Firmware heap placement is kernel-only and should not be exposed to userspace.

Dependencies and integration points: Includes `linux/sizes.h`. Integrates with DRM GEM/device memory managers, userspace VA allocation, PDS/USC code upload, region header allocation, transfer/fragment resources, visibility tests, and firmware memory setup.

Risks: Overlapping or moving heaps breaks userspace ABI and can corrupt GPU VA mappings. Bases must remain 4 MiB aligned and avoid zero. The BRN63142 region-header placement is a workaround-sensitive constraint. Comments show some free/reserved region ranges and sizes that should be checked carefully when extending the map.

Test signals: VA allocator tests for every heap, overlap/alignment assertions, userspace mmap/bind tests, PDS/USC execution tests, region-header BRN63142 regression, firmware heap isolation tests, and memory-context creation across 40-bit VA boundaries.
