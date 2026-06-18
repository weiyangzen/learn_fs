# sources/distributed-fs/ceph-client/drivers/nvdimm/label.h

## Purpose
`label.h` defines the persistent namespace label formats and label-management API for libnvdimm. It covers UEFI namespace indexes, EFI namespace labels, CXL region and namespace labels, known abstraction GUID/UUID strings, label flags, and helper declarations used by label, DIMM, namespace, and BTT code.

## Important APIs, Types, And Constants
Important constants include namespace-index signature and alignment values, label UUID/name sizes, `NSLABEL_FLAG_ROLABEL`, `NSLABEL_FLAG_LOCAL`, `NSLABEL_FLAG_BTT`, `NSLABEL_FLAG_UPDATING`, BTT info constants, label minimum size, and known GUID/UUID strings for BTT, BTT2, PFN, DAX, CXL region, and CXL namespace.

Persistent structures are `struct nd_namespace_index`, `struct cxl_region_label`, `struct nvdimm_efi_label`, `struct nvdimm_cxl_label`, and the union wrapper `struct nd_namespace_label`. `struct nd_label_id` holds resource names such as `pmem-<namespace uuid>`.

The inline `nd_label_next_nsindex()` returns the alternate index for copy-on-write updates, or `-1` when no valid index exists. Declared APIs include label-data initialization, index sizing, active-label iteration, slot allocation/free, free count, and `nd_pmem_namespace_label_update()`.

## Control Flow
This header does not perform runtime control flow beyond `nd_label_next_nsindex()`. Its layouts drive validation and updates in `label.c`: namespace index blocks describe the active label array and free bitmap, while namespace labels describe per-DIMM pieces of a namespace and their claim personality.

## State And Persistence Behavior
All major structures in this file are on-media config-data formats. `nd_namespace_index` is the label set superblock with sequence, offsets, size, checksum, and free bitmap. EFI labels carry namespace UUID/name, flags, interleave information, DPA range, slot, optional type/abstraction GUIDs, and checksum. CXL labels use CXL table layouts and UUIDs for type/abstraction identities.

Because these layouts are persistent ABI, field order, sizes, endianness annotations, and reserved bytes are compatibility-sensitive. The `NSLABEL_FLAG_UPDATING` flag is part of the update protocol.

## Dependencies And Integration Points
The header depends on `linux/ndctl.h`, sizes, UUID/GUID, and I/O types. It is included by `nd.h` for label accessors, `label.c` for validation/update logic, `dimm.c`/`dimm_devs.c` for label storage handling, and `namespace_devs.c` for namespace construction and updates.

## Risks And Edge Cases
Persistent structure changes can break existing DIMM labels. EFI label fields past `align` must be gated by `efi_namespace_label_has()` in `nd.h`, because older label sizes do not contain later fields. CXL and EFI labels differ in semantics; code must not assume interleave cookies or GUID fields exist for CXL. The free bitmap may include padding bits that must remain zero.

## Test Signals
Tests should validate exact structure sizes for supported label versions, namespace-index free bitmap rounding, alternate-index selection, EFI v1.1/v1.2 field availability, CXL label parsing, GUID/UUID constant parsing, and update behavior involving `NSLABEL_FLAG_UPDATING`.
