<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c

## Purpose

`kfd_crat.c` parses and synthesizes CRAT topology data for KFD. It converts compute, memory, cache, and IO-link subtype records into `kfd_topology_device` properties and creates virtual CRAT images for CPUs or discrete GPUs when firmware/ACPI does not provide one.

## Important APIs, Types, and Entry Points

- `kfd_parse_crat_table()` creates topology devices for CRAT domains, copies OEM metadata, walks enabled subtype records, and dispatches parsers.
- `kfd_create_crat_image_virtual()` allocates CPU or GPU virtual CRAT images; `kfd_destroy_crat_image()` frees them.
- `kfd_get_gpu_cache_info()` selects static cache tables or fills cache records from AMDGPU IP-discovery config.
- Subtype parsers attach CU, memory, cache, and IO-link records to topology device lists.
- CPU VCRAT helpers emit per-NUMA compute, memory, and CPU-to-CPU IO-link records.
- GPU VCRAT helpers emit one GPU compute-unit record, VRAM memory record, GPU-to-CPU link, and XGMI peer links.

## Control Flow

Parsing starts with a non-null image and an empty output list. The parser creates one topology device per CRAT domain, assigns sequential proximity domains from the caller's base, then walks subtype records until the CRAT image length is reached. Enabled records are parsed by type; TLB and CCompute are currently logged and ignored, and unknown subtypes warn without failing.

CU records populate CPU core counts/base IDs or GPU SIMD/LDS/wave/CU-layout fields. Memory records map CPU nodes to system heaps and GPU nodes to framebuffer public/private heaps, aggregating banks with matching heap type, flags, and width. Cache records map by processor/SIMD ID ranges because cache subtypes do not carry proximity domains. IO-link records create link properties and clone a reverse link when bidirectional.

Virtual CPU CRAT creation uses online NUMA nodes, DSDT OEM metadata, APIC IDs, managed page counts, and x86 CPU-vendor link types. Virtual GPU CRAT creation uses AMDGPU GFX/CU/local-memory data, large-BAR state, PCIe or XGMI bandwidth, SRAT NUMA lookup, hive ID, and already-created topology peers to describe the GPU node.

Cache selection keys first on legacy `asic_type`, then on `KFD_GC_VERSION()`. Older devices use static arrays; GC 9.4.3/9.4.4/9.5 and GC11/GC12 style devices can derive records from `adev->gfx.config` and `adev->gmc.mall_size`. Unknown hardware gets dummy cache info with a warning.

## State and Persistence Behavior

The global `gpu_processor_id_low` monotonically assigns synthetic GPU processor/SIMD ID ranges for virtual GPU CRATs. Generated CRAT images are temporary heap allocations; persistent state is the topology list and its memory/cache/IO-link property lists. IO-link bidirectionality is materialized as two list entries. Cache info is either static read-only data or caller-provided writable storage populated from AMDGPU config.

## Dependencies and Integration Points

The file depends on `kfd_crat.h`, KFD topology allocation/release helpers, KFD node/device structures, AMDGPU ASIC/IP-discovery fields, local memory info, XGMI bandwidth/hops/sharing helpers, PCI/ACPI/NUMA APIs, and `kfd_dev_is_large_bar()`. The parsed topology feeds KFD/HSA topology sysfs and runtime device discovery.

## Risks and Edge Cases

- Subtype stepping trusts `length`; malformed zero or short lengths can break parser progress or casts.
- Cache parsing depends on CU records having been parsed first.
- OEM metadata is copied only to the last created topology device in the current parser flow.
- Dynamic cache fill expects `*pcache_info` to point at valid writable storage.
- GPU VCRAT uses fixed `4 * PAGE_SIZE`; many future records or peer links can overflow and return `-ENOMEM`.
- Bidirectional link cloning requires the destination topology device to already exist.
- SRAT fallback may approximate bad firmware bindings as NUMA node 0.
- Dummy cache fallback keeps unknown hardware usable but exposes inaccurate cache hierarchy.

## Test and Validation Signals

Validate parser cleanup and malformed subtype handling, CU/memory/cache/IOLINK property population, memory-bank aggregation, bidirectional link cloning, CPU VCRAT on single and multi-node NUMA systems, GPU VCRAT for large/small BAR and XGMI/PCIe paths, and cache-info selection across legacy, dynamic, and unknown IP versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.c -->
