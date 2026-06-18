# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.h

## Purpose
This header defines the host-side CPD firmware container ABI used by IPU6 firmware validation and package-directory creation.

## Important APIs, types, and definitions
Constants define string/field sizes, metadata extension/image types, package directory server indices, client package type, and hash sizes for IPU6 and IPU6SE. ABI structs include `ipu6_cpd_module_data_hdr`, packed `ipu6_cpd_hdr`, `ipu6_cpd_ent`, metadata component headers and component variants, metadata extension, and client package header. Public functions are `ipu6_cpd_create_pkg_dir()`, `ipu6_cpd_free_pkg_dir()`, and `ipu6_cpd_validate_cpd_file()`.

## Control flow and integration points
`ipu6-cpd.c` uses these definitions to walk firmware blobs, while `ipu6.c` invokes validation/package setup during firmware load. Buttress authentication ultimately consumes the DMA package directory built from these ABI records.

## State, persistence, and dependencies
The header has no mutable state; its packed layouts are persisted in firmware files and must match CSE/IPU firmware expectations. It forward-declares `ipu6_device` and `ipu6_bus_device` for public APIs.

## Risks and test signals
Risks are ABI layout drift, wrong packing, incorrect hash-size selection for IPU6SE, or constants that no longer match firmware images. Test signals are firmware validation on all supported IPU6 variants, static layout checks if added, and negative tests for malformed CPD files.
