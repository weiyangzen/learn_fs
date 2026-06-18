# sources/distributed-fs/ceph-client/include/linux/iommu-debug-pagealloc.h

Purpose: This header exposes optional IOMMU debug-pagealloc checks that validate pages are unmapped before page allocation debugging frees or reuses them.

Important APIs, types, and functions: Under `CONFIG_IOMMU_DEBUG_PAGEALLOC`, it declares the static key `iommu_debug_initialized`, page extension operations `page_iommu_debug_ops`, and `__iommu_debug_check_unmapped`. The inline `iommu_debug_check_unmapped` calls the heavy checker only when the static key is enabled. Disabled builds provide an empty inline.

Control flow: Callers invoke the inline check with a page and page count. Static-branch gating avoids overhead until debug tracking is initialized.

State and persistence: State is external: static key initialization and page extension metadata track mapping state. The header owns no storage in disabled builds.

Dependencies and integration points: Integrates IOMMU API state with page extension/pagealloc debug infrastructure and static keys.

Risks: False positives can panic or warn during legitimate delayed unmap flows; false negatives miss DMA/IOMMU leaks. The checker must only be active after metadata is initialized.

Test signals: Build with debug enabled/disabled, validate static key transition, free mapped and unmapped pages, multi-page ranges, and page extension registration ordering.
