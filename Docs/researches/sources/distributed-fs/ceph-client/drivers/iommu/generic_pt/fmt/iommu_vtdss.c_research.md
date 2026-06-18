# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_vtdss.c

## Purpose

`iommu_vtdss.c` instantiates the Generic PT IOMMU template for Intel VT-d second-stage page tables.

## Important APIs, Types, and Functions

- `#define PT_FMT vtdss`: selects `fmt/vtdss.h`.
- `PT_SUPPORTED_FEATURES`: enables VT-d second-stage force-coherence, force-writeable erratum handling, and DMA-incoherent handling.
- Inclusion of `iommu_template.h`: generates VT-d second-stage operations.

## Control Flow

The wrapper delegates all runtime behavior to generated template code. The selected features affect protection conversion and cache-maintenance behavior during mapping.

## State and Persistence Behavior

State is in generated `pt_iommu_vtdss` objects and VT-d second-stage PTE tables. Force-writeable and force-coherence features alter descriptor bits, not separate state.

## Dependencies and Integration Points

It is selected by Intel IOMMU support and used for nested/second-stage translation roots.

## Risks and Edge Cases

The force-writeable feature rejects read-only mappings for erratum-sensitive parent domains. DMA-incoherent support requires a valid IOMMU device in the generated table.

## Test Signals

KUnit should cover 3-, 4-, and 5-level tables, read-only rejection when force-writeable is active, dirty tracking, and hardware-info `ssptptr/aw` output.
