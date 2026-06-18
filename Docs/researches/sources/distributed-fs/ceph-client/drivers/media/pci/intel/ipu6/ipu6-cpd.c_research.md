# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-cpd.c

## Purpose
This file validates Intel CPD firmware containers and builds the IPU package directory consumed by secure firmware boot/authentication. It extracts manifest, metadata, and module-data entries, validates size/layout/type constraints, and creates a DMA-visible package directory containing component addresses, sizes, IDs, versions, manifest, and metadata.

## Important APIs, types, and functions
`ipu6_cpd_validate_cpd_file()` is the public validator. It calls `ipu6_cpd_validate_cpd()`, checks the `$CPD` marker, validates manifest size, validates metadata with `ipu6_cpd_validate_metadata()`, and validates module data with `ipu6_cpd_validate_moduledata()`. `ipu6_cpd_create_pkg_dir()` allocates package-directory memory with `ipu6_dma_alloc()`, parses module data via `ipu6_cpd_parse_module_data()`, copies manifest and metadata, and syncs the allocation. `ipu6_cpd_free_pkg_dir()` releases the DMA buffer. Helpers retrieve CPD entries and metadata component IDs/versions.

## Control flow and integration points
The PCI core validates the firmware file after request_firmware and later creates a package directory for PSYS. Buttress authentication writes the package directory DMA address to firmware source registers. The parser uses metadata component IDs/versions to encode package directory entries and module-data CPD offsets to compute DMA addresses relative to the mapped firmware image.

## State, persistence, and dependencies
State is stored in `adev->pkg_dir`, `adev->pkg_dir_dma_addr`, and `adev->pkg_dir_size` until freed. Validation depends on `isp->cpd_metadata_cmpnt_size`, which differs between IPU6 variants. The code depends on bitfield helpers, DMA allocation wrappers, CPD ABI structs, and IPU6 bus/device state.

## Risks and test signals
Risks are unchecked integer/offset assumptions, malformed firmware with inconsistent CPD header lengths, component metadata-size mismatches, package-directory overflow beyond 15 entries plus header, and wrong component ID/version encoding. Test signals include valid firmware load, rejected corrupted headers/offsets/metadata, package directory DMA sync before authentication, no leaks on parse failure, and CSE authentication using the generated directory.
