# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_hal.h

## Purpose
`icp_qat_hal.h` defines low-level QAT accelerator-engine and firmware-control-unit CSR offsets, status/command enums, bit masks, timing constants, MMIO address calculations, and CSR access macros used by firmware loader HAL code.

## Important APIs, Types, And Functions
Important enums are `hal_global_csr`, generation-specific global CSR offsets, `hal_ae_csr`, `fcu_csr`, `fcu_csr_4xxx`, `fcu_cmd`, and `fcu_sts`. Macros define AE masks, context enable bits, local memory/global mode bits, wakeup events, FCU status positions, authentication retry timing, MMIO region offsets, and accessors such as `SET_CAP_CSR()`, `GET_CAP_CSR()`, `AE_CSR_ADDR()`, `SET_AE_CSR()`, `GET_AE_CSR()`, `AE_XFER_ADDR()`, `SET_AE_XFER()`, and `SRAM_WRITE()`.

## Control Flow
No functions are implemented here. Loader code uses these definitions to reset AEs, enable clocks, write ustore/local memory/registers, start or authenticate firmware through the FCU, poll status, and address per-AE local and transfer CSRs.

## State And Persistence Behavior
The header owns no software state. It defines how `icp_qat_fw_loader_handle` MMIO base pointers are interpreted and how writes affect persistent device state until reset or driver teardown.

## Dependencies And Integration Points
It includes `icp_qat_fw_loader_handle.h`, uses `ADF_CSR_RD/WR`, and is tightly coupled to firmware loader code, chip generation metadata, and PCI BAR mappings.

## Risks
These macros can write device control registers directly; wrong offsets or AE IDs can hang firmware loading or reset active engines. Generation-specific offsets must be selected correctly. Polling constants such as authentication retry periods affect boot latency and failure detection.

## Test Signals
Firmware load/auth/start on each supported generation, AE reset/restart, ustore programming validation, and FCU status transitions are the main signals. CSR trace logs can confirm expected offsets and commands.
