# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_amdv1.c

## Purpose

`iommu_amdv1.c` is the AMDv1 wrapper that instantiates the shared `iommu_pt.h` template with AMDv1 format definitions.

## Important APIs, Types, and Functions

- `#define PT_FMT amdv1`: selects `fmt/amdv1.h`.
- `PT_SUPPORTED_FEATURES`: enables AMDv1 force-coherence, AMDv1 encrypted tables, dynamic top growth, and DMA-incoherent page-table handling.
- Inclusion of `iommu_template.h`: expands the format-specific Generic PT IOMMU implementation.

## Control Flow

The wrapper contains no runtime control flow of its own. Compilation sets preprocessor knobs and then includes the template, generating AMDv1-namespaced init, map, unmap, dirty, info, deinit, and hardware-info symbols.

## State and Persistence Behavior

State is whatever the template and `amdv1.h` generate in `struct pt_iommu_amdv1`. The wrapper only controls feature availability at compile time.

## Dependencies and Integration Points

It depends on `amdv1.h`, `iommu_template.h`, Kbuild format selection, and consumers that link to the exported `GENERIC_PT_IOMMU` namespace symbols.

## Risks and Edge Cases

Incorrect `PT_SUPPORTED_FEATURES` would silently remove support expected by AMD users. Dynamic top requires driver callbacks at runtime; DMA-incoherent requires an IOMMU device for cache maintenance.

## Test Signals

Build the AMDv1 module and run the AMDv1 KUnit suite under normal and debug configurations, including dynamic-top and DMA-incoherent feature toggles where supported.
