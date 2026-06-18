# sources/distributed-fs/ceph-client/drivers/nvdimm/nd.h

## Purpose
`nd.h` is the main private libnvdimm type and helper header shared by namespace, DIMM, region, label, BTT, PFN, and DAX code. It defines core runtime structures, label field accessors for EFI versus CXL formats, region/mapping state, claim-device structures, feature stubs, and many cross-file function prototypes.

## Important APIs, Types, And Declarations
Major types include `struct nvdimm_drvdata`, `struct nd_region_data`, `struct nd_mapping`, `struct nd_region`, `struct nd_btt`, `struct nd_pfn`, `struct nd_dax`, and generic `struct nd_gen_sb`. Important enums include NVDIMM I/O constants, label flags, mapping lock classes, PFN modes, and async modes.

The header provides many static inline label accessors: `nsl_get/set_name`, slot, checksum, flags, DPA, rawsize, isetcookie, position, nlabel, nrange, LBA size, UUID, and raw UUID bytes. These hide EFI/CXL label layout differences. Other inlines include namespace index pointer helpers, `efi_namespace_label_has()`, DPA iteration macros, `nsl_validate_nlabel()`, `nd_inc_seq()`, `nd_info_block_reserve()`, and `is_bad_pmem()`.

Function declarations cover device registration, DIMM config data, security, BTT/PFN/DAX creation/probe/validation, region namespace registration, bus locking, DPA allocation, namespace capacity/locking/probe, badblock population, namespace enable/disable, PFN setup, region activation, disk naming, sector size, and pmem page-mapping policy.

## Control Flow
The header centralizes cross-file control contracts. For example, namespace code uses label accessors to interpret active labels, label code uses region/mapping definitions to persist updates, BTT/PFN/DAX wrappers use claim-device structures, and bus code uses registration prototypes. Feature-conditioned inline stubs return clean failure values when BTT/PFN/DAX/claim support is disabled.

The label accessor flow is especially important: callers pass `nvdimm_drvdata`, and the accessor chooses CXL or EFI fields based on `ndd->cxl`. This avoids scattering format checks across allocation and discovery code.

## State And Persistence Behavior
`struct nvdimm_drvdata` caches persistent label storage (`data`), namespace-area geometry, EFI/CXL label size mode, current/next namespace indexes, and the volatile DPA resource root. `struct nd_region` holds persistent-memory region geometry, mappings, badblocks, seed devices, lane state, and flush operation. `struct nd_btt`, `struct nd_pfn`, and `struct nd_dax` hold claim personality configuration backed by persistent info blocks or labels.

`struct nd_gen_sb` defines the common 4 KiB checksum shape for BTT/PFN info blocks. Label accessors read and write little-endian persistent fields and must preserve ABI-specific differences.

## Dependencies And Integration Points
`nd.h` depends on public libnvdimm, badblocks, block device, device, mutex, ndctl, types, and `label.h`. It is included by almost every libnvdimm implementation file and bridges to external PMEM, region, PFN, DAX, and security code not all present in this subset.

## Risks And Edge Cases
Inline helper mistakes propagate broadly and may corrupt persistent labels. `efi_namespace_label_has()` must gate access to newer EFI label fields for older label sizes. `nd_inc_seq()` encodes the namespace-index sequence cycle used for copy-on-write persistence; changing it breaks index selection. Optional stubs must preserve caller semantics for disabled configs. `is_bad_pmem()` assumes 512-byte sector units for badblock queries.

## Test Signals
Tests should cover EFI and CXL label accessor round trips, old EFI label-size field gating, namespace-index pointer math, DPA iteration macros, sequence progression, BTT/PFN/DAX config-off builds, badblock checks, claim personality structure layout expectations, and region/mapping state consumed by namespace discovery and DPA allocation.
