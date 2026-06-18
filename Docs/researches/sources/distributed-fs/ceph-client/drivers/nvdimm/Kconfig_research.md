# sources/distributed-fs/ceph-client/drivers/nvdimm/Kconfig

## Purpose
Defines build configuration for the libnvdimm subsystem, persistent memory block devices, BTT, PFN, DAX, device-tree PMEM, RAMDAX, key/security support, KMSAN interaction, and unit-test build helpers.

## Important APIs, Types, And Functions
No runtime APIs. Key symbols:
- `LIBNVDIMM`: top-level NVDIMM support, requiring 64-bit physical addresses, I/O memory, and block layer.
- `BLK_DEV_PMEM`: PMEM block device and DAX-capable namespace support.
- `BTT` / `ND_BTT`: block translation table support for atomic sector semantics.
- `NVDIMM_PFN` / `ND_PFN`: struct-page support for persistent memory.
- `NVDIMM_DAX`: raw device-DAX namespace access.
- `OF_PMEM` and `RAMDAX`: non-ACPI persistent memory descriptions.
- `NVDIMM_KEYS`, `NVDIMM_KMSAN`, `NVDIMM_TEST_BUILD`, and `NVDIMM_SECURITY_TEST`: security/debug/test integration.

## Control Flow
Kconfig dependency and select relationships determine which object groups the Makefile builds and which features are reachable. Most feature symbols live under `if LIBNVDIMM`.

## State And Persistence
Build-time configuration only. Runtime persistent-memory behavior is determined by selected symbols.

## Dependencies And Integration Points
Integrates with block, DAX, ZONE_DEVICE, encrypted keys, KMSAN, OF, e820/legacy PMEM, and compile-test infrastructure.

## Risks And Edge Cases
- `NVDIMM_KMSAN` warns about permanent capacity impact because `struct page` metadata stored in pmem can grow with memory-debug options.
- Security-test options alter cache-maintenance behavior for unit tests and should stay off for normal systems.
- Defaults choose many features when `LIBNVDIMM` is enabled, so minimal builds must opt out deliberately.

## Test Signals
Configuration tests should verify symbol visibility under dependencies, default selections, and module/built-in combinations. Compile tests should cover `NVDIMM_TEST_BUILD` on x86_64 `COMPILE_TEST`.
