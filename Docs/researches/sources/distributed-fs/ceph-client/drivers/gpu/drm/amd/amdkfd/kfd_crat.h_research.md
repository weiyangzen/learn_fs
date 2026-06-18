<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h

## Purpose

`kfd_crat.h` defines the packed CRAT binary-layout structures, subtype IDs, flags, IO-link constants, GPU cache-info helper type, and KFD CRAT helper prototypes used by KFD topology parsing and virtual CRAT generation.

## Important APIs, Types, and Entry Points

- `struct crat_header` describes CRAT signature, length, OEM metadata, entry count, and domain count.
- Packed subtype records cover compute unit, memory, cache, TLB, CCompute, IO-link, and generic subtype headers.
- Flags describe enabled records, CPU/GPU/IOMMU presence, memory volatility, cache/TLB type, IO-link coherency/atomics/peer-DMA, and bidirectionality.
- `CRAT_SIBLINGMAP_SIZE` is fixed at 32 bytes and documented as ABI-sensitive.
- IO-link type constants include PCIe, XGMI, coherent fabric, RDMA, and generic transport types.
- `struct kfd_gpu_cache_info` is the compact internal descriptor used to generate GPU cache records.
- Prototypes expose `kfd_get_gpu_cache_info()`, `kfd_parse_crat_table()`, `kfd_create_crat_image_virtual()`, and `kfd_destroy_crat_image()`.

## Control Flow

Consumers cast a CRAT image to `struct crat_header`, then iterate packed records using `struct crat_subtype_generic.type` and `length`. Virtual CRAT generation fills the same packed structures and later frees the allocated image through the destroy helper. `#pragma pack(1)` ensures `sizeof()` and field offsets match the serialized table layout expected by the parser.

## State and Persistence Behavior

The header stores no runtime state, but it defines ABI-persistent binary layout. Changing structure order, field sizes, subtype IDs, flag values, or `CRAT_SIBLINGMAP_SIZE` changes how firmware or virtual CRAT images are interpreted. `struct kfd_gpu_cache_info` persists internal cache metadata used to emit CRAT cache subtypes.

## Dependencies and Integration Points

The header depends on Linux integer types and forward-declares `struct kfd_node`. It is included by CRAT generation/parsing code and topology initialization, and its records ultimately feed KFD/HSA topology information consumed by userspace runtimes.

## Risks and Edge Cases

- Subtype `length` is `uint8_t`; record sizes must remain within 255 bytes.
- Packed structures can be unaligned, so accessors must not assume natural alignment.
- Changing `CRAT_SIBLINGMAP_SIZE` would break cache/TLB record ABI.
- IO-link bidirectionality uses bit 31, so masking/sign mistakes can drop reverse links.
- The misspelled `max_slots_scatch_cu` field is part of the C source contract even though the binary layout is what matters.

## Test and Validation Signals

Use compile-time `sizeof()`/offset checks for packed records, parser fixtures for every subtype/flag family, and regression tests ensuring sibling-map size, subtype IDs, IO-link type values, and emitted `length` fields do not drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_crat.h -->
