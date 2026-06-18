# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_loader_handle.h

## Purpose
`icp_qat_fw_loader_handle.h` defines top-level state objects used by the QAT firmware loader and HAL. It captures per-AE loader state, chip capability/register metadata, MMIO mappings, object handles, and firmware DRAM descriptors.

## Important APIs, Types, And Functions
Important structures are `icp_qat_fw_loader_ae_data`, `icp_qat_fw_loader_hal_handle`, `icp_qat_fw_loader_chip_info`, `icp_qat_fw_loader_handle`, and `icp_firml_dram_desc`. Fields track AE masks, admin AE masks, slice masks, revision, ustore sizes, reset delays, local memory size, reset/clock/FCU CSR offsets, firmware-authentication features, CSS variant flags, PCI device, UOF/SUOF/MOF object handles, and mapped SRAM/CAP/EP CSR regions.

## Control Flow
The header has no executable control flow. Loader code initializes these structures, maps MMIO regions, parses firmware objects, configures chip-specific CSR offsets, loads/authenticates firmware through HAL/FCU paths, and frees mappings during teardown.

## State And Persistence Behavior
The handle persists for the firmware loading lifetime of an accelerator. AE data records free ustore ranges, live contexts, and AE state. Chip info is effectively static per hardware generation. DRAM descriptors persist while firmware image staging memory is allocated.

## Dependencies And Integration Points
It includes `icp_qat_uclo.h` for firmware object structures and is included by `icp_qat_hal.h`. It integrates PCI, MMIO CSR access, firmware object parsing, authentication, and accelerator engine state management.

## Risks
Chip-specific offsets and flags must match hardware generation; wrong values can reset or program the wrong CSR. AE masks and ustore sizes gate firmware placement, so inconsistencies can corrupt AE instruction store. Firmware authentication flags (`fw_auth`, `css_3k`, `dual_sign`) must align with the image format.

## Test Signals
Firmware load success, AE live context masks, authenticated image status, FCU load/auth completion, and unload/reload cycles validate these structures. Multi-generation tests should cover classic, 4xxx/6xxx, CSS 2K/3K, and dual-sign firmware metadata.
