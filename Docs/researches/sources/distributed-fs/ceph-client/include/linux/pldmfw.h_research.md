# sources/distributed-fs/ceph-client/include/linux/pldmfw.h

## Purpose
the PLDM firmware-update library interface. It describes firmware package parsing, component
matching, flash-update callbacks, and transfer progress plumbing for devices that consume PLDM
firmware images.

## Important APIs, types, and functions
Macros/constants: `_PLDMFW_H_`, `PLDM_DEVICE_UPDATE_CONTINUE_AFTER_FAIL`,
`PLDM_STRING_TYPE_UNKNOWN`, `PLDM_STRING_TYPE_ASCII`, `PLDM_STRING_TYPE_UTF8`,
`PLDM_STRING_TYPE_UTF16`, `PLDM_STRING_TYPE_UTF16LE`, `PLDM_STRING_TYPE_UTF16BE`,
`PLDM_DESC_ID_PCI_VENDOR_ID`, `PLDM_DESC_ID_IANA_ENTERPRISE_ID`, `PLDM_DESC_ID_UUID`,
`PLDM_DESC_ID_PNP_VENDOR_ID`, `PLDM_DESC_ID_ACPI_VENDOR_ID`, `PLDM_DESC_ID_PCI_DEVICE_ID`, and 31
more. Types: `struct pldmfw_record`, `struct pldmfw_desc_tlv`, `struct pldmfw_component`, `struct
pldmfw`, `struct pldmfw_ops`, `enum pldmfw_update_mode`. Declared or inline functions:
`pldmfw_op_pci_match_record`, `bool`, `int`, `pldmfw_flash_image`. Important struct details: struct
pldmfw_record fields include `struct list_head entry`, `struct list_head descs`, `const u8
*version_string`, `u8 version_type`, `u8 version_len`, `u16 package_data_len`, `u32
device_update_flags`, `const u8 *package_data`; struct pldmfw_desc_tlv fields include `struct
list_head entry`, `const u8 *data`, `u16 type`, `u16 size`; struct pldmfw_component fields include
`struct list_head entry`, `u16 classification`, `u16 identifier`, `u16 options`, `u16
activation_method`, `u32 comparison_stamp`, `u32 component_size`, `const u8 *component_data`; struct
pldmfw fields include `const struct pldmfw_ops *ops`, `struct device *dev`, `u16
component_identifier`, `enum pldmfw_update_mode mode`; struct pldmfw_ops fields include `bool
(*match_record)(struct pldmfw *context, struct pldmfw_record *record)`, `int
(*send_package_data)(struct pldmfw *context, const u8 *data, u16 length)`, `u8 transfer_flag)`, `int
(*flash_component)(struct pldmfw *context, struct pldmfw_component *component)`, `int
(*finalize_update)(struct pldmfw *context)`. Important enum details: enum pldmfw_update_mode values
include `PLDMFW_UPDATE_MODE_FULL`, `PLDMFW_UPDATE_MODE_SINGLE_COMPONENT`.

## Control flow
A device driver supplies `struct pldmfw_ops` and private context, then calls the PLDM firmware
helper with a firmware blob. The helper parses the package, matches descriptors against the device,
requests component-table decisions, streams component payloads through the driver's write hooks, and
reports progress or cancellation through the callback table.

## State and persistence
The header stores no data itself; firmware-update state lives in the caller context and parser-owned
transfer state while an update is in progress. Component identity, package metadata, cancellation
state, and written bytes are transient unless the driver's flash operation commits them to device
storage.

## Dependencies and integration points
It includes `linux/list.h`, `linux/firmware.h`. Direct source-tree consumers found by include search
are `sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/meta/fbnic/fbnic_devlink.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/intel/ixgbe/ixgbe_fw_update.c`, `sources/distributed-fs/ceph-
client/drivers/net/ethernet/intel/ice/ice_fw_update.c`. It integrates with the Linux driver core and
in-kernel helper libraries that include this header.

## Risks and test signals
Risks include accepting an incompatible component image, descriptor matching mistakes, integer
overflows in package offsets and sizes, partial flash writes after cancellation, and callback
implementations that sleep or fail in unsupported contexts. Test signals include malformed PLDM
packages, descriptor mismatch, multi-component updates, cancellation, progress accounting, and
injected flash-write failures.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/pldmfw.h` completely for this pass (173 lines, 5032 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/pldmfw.h_research.md`.
