# sources/distributed-fs/ceph-client/include/asm-generic/agp.h

Purpose: Supplies minimal generic AGP cache/page hooks for architectures that do not need special AGP mapping operations.

Important APIs, types, and functions: Defines `map_page_into_agp(page)` and `unmap_page_from_agp(page)` as no-ops, and `flush_agp_cache()` as `mb()`.

Control flow: No branch logic; callers get a memory barrier for cache flush and no page-specific setup.

State and persistence: No state.

Dependencies and integration points: Includes `asm/io.h` for barrier/I/O context. Integrates with AGP/GART graphics memory paths on simple architectures.

Risks and test signals: Risks are using this fallback on hardware requiring explicit cache management or AGP aperture mapping. Test AGP graphics workloads, DMA coherency, and architecture overrides for non-coherent systems.
