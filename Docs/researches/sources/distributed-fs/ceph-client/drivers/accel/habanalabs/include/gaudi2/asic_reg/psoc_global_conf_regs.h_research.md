<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h

## Purpose
`psoc_global_conf_regs.h` is the Gaudi2 PSOC global configuration address map. It is auto-generated, guarded by `ASIC_REG_PSOC_GLOBAL_CONF_REGS_H_`, and exports 658 `mmPSOC_GLOBAL_CONF_*` addresses from `0x4C4B000` through `0x4C4BE70`. The block covers boot/reset control, firmware communication, scratchpads, semaphores, trace identity, interrupts, boot media, pad controls, isolation controls, ASIF plumbing, ADC, scrambling, and DFT.

## Important APIs, Types, And Functions
No executable APIs are declared. Important address groups include:

- `NON_RST_FLOPS_*`, `COLD_RST_FLOPS_*`, `SCRATCHPAD_0..31`, and `SEMAPHORE_0..31`.
- Boot/reset/FSM registers such as `PCI_FW_FSM`, `BOOT_SEQ_RE_START`, `BTM_FSM`, `SW_BTM_FSM`, `BOOT_SEQ_FSM`, timeouts, reset delays, reset source/state/masks, and boot image/status registers.
- Firmware and trace registers: `CPU_BOOT_STATUS`, `KMD_MSG_TO_CPU`, `TRACE_ADDR`, `TRACE_AXPROT`, `TRACE_AWUSER`, and `TRACE_ARUSER`.
- Error/interrupt/status registers: RAZWI, timeout/peripheral/AXI/watchdog, SMB alert, PCIe PSOC DERR, SPI write-without-order, ASIF function/error, and ASIF master status/error.
- IO/fabric families: I2C, SPI/QSPI/SPI DMA/BSAC, boot straps, pad 1.8V/3.3V/default/select arrays, isolation controls, ASIF request/response queues, ADC arrays, scrambling polynomial registers, and DFT control.

## Control Flow
The header itself has no logic. Gaudi2 runtime code reads and writes these addresses during firmware load, boot-status polling, reset/restart, CoreSight trace setup, RAZWI handling, and security checks. For example, `gaudi2.c` records `mmPSOC_GLOBAL_CONF_CPU_BOOT_STATUS` and `mmPSOC_GLOBAL_CONF_KMD_MSG_TO_CPU` for firmware interfaces, reads `BTM_FSM`, configures trace address/AXUSER registers through CoreSight paths, and reads RAZWI interrupt/mask info for diagnostics.

## State And Persistence
The register block mixes volatile status with reset-domain persistence. Scratchpads and non-reset flops can retain values across some reset paths and are used for firmware/driver handoff. Boot FSM, reset source, interrupt causes, pad configuration, isolation, ASIF queues, and trace settings are hardware state and may be firmware-owned, driver-owned, or shared depending on lifecycle phase.

## Dependencies
Runtime consumers depend on `psoc_global_conf_masks.h`, Gaudi2 boot/reset/security/CoreSight code, firmware protocols, and generated base range definitions. Address correctness is also security-sensitive because PSOC global config contains scratchpads and control registers used during privileged flows.

## Integration Points
This header integrates with Gaudi2 firmware loading, static loader metadata, pre-firmware boot status polling, reset machinery, CoreSight ETR buffer addressing and AXUSER setup, RAZWI diagnostics, and security register-range validation.

## Risks
Wrong addresses can break boot or reset, write firmware messages to the wrong register, misreport errors, or corrupt pad/isolation controls. The repeated pad/default/scrambling/ADC arrays are vulnerable to stride/count assumptions. Shared scratchpad and persistent registers require careful ownership because writes can affect firmware state beyond the current driver call.

## Test Signals
Signals include boot and firmware-load success, reset-source correctness, BTM/boot FSM expected states, KMD-to-CPU messaging, CoreSight trace setup, RAZWI reporting, scratchpad access policy tests, interrupt handling, and generated-address comparison against the Gaudi2 register database.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_regs.h -->
