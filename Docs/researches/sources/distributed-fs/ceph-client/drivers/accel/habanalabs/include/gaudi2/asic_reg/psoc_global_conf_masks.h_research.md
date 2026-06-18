<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h

## Purpose
`psoc_global_conf_masks.h` defines field masks and shifts for the Gaudi2 PSOC global configuration block. It is paired with `psoc_global_conf_regs.h`, guarded by `ASIC_REG_PSOC_GLOBAL_CONF_MASKS_H_`, and exports 937 macros covering reset/boot sequencing, persistent flops, scratchpads, semaphores, trace configuration, interrupts, SPI/QSPI/BSAC controls, strap pins, isolation controls, ASIF request/response plumbing, pad configuration, scrambling, ADC, and DFT controls.

## Important APIs, Types, And Functions
There are no functions or types. Major field families include:

- Boot/reset: `BOOT_SEQ_RE_START`, `BTM_FSM`, `BOOT_SEQ_FSM`, timeout, reset indicators, reset source, reset masks, boot state, and boot-loader image/status fields.
- Firmware communication and persistence: `NON_RST_FLOPS`, `COLD_RST_FLOPS`, `SCRATCHPAD`, `SEMAPHORE`, `CPU_BOOT_STATUS`, and `KMD_MSG_TO_CPU`.
- Error/interrupt: RAZWI interrupt and mask info, timeout/peripheral/AXI/watchdog interrupts, PCIe PSOC DERR controls, SMB alert, SPI write-without-order interrupts, and ASIF functional/error interrupt fields.
- Trace/MMU identity: `TRACE_ADDR_MSB`, `TRACE_AXPROT`, `TRACE_AWUSER`, `TRACE_ARUSER`, scrambling controls and polynomial fields.
- Boot media and low-speed IO: SPI/QSPI selection, SPI DMA, direct write/read, BSAC, boot strap pins, I2C debug/slave, EMMC voltage, ADC configuration and data.
- Fabric/pad/isolation: ARC LBU AXI split controls, master interface controls, target ID, pad 1.8V/3.3V/default/select arrays, TPC/VDEC/NIC/MME/EDMA/HBM/XBAR/HIF-HMMU isolation, and ASIF master/core request/response/status/debug fields.

## Control Flow
The header is declarative. Runtime control flow in Gaudi2 code reads boot status, sends KMD messages to firmware, restarts boot sequencing, checks BTM FSM state, configures trace AXUSER/ARUSER/AWUSER and trace address fields, decodes RAZWI mask info, and controls reset-related fields. The masks are also used with `FIELD_GET` to format diagnostic information from RAZWI and boot/reset registers.

## State And Persistence
This block contains both volatile status and reset-persistent state. Non-reset flops and scratchpads intentionally survive some reset classes and may communicate boot/firmware state. Cold reset flops, reset-source indicators, boot FSMs, interrupt causes, semaphores, trace address and AXUSER settings, pad configuration, and isolation controls are hardware state with lifetimes defined by reset domain and firmware/driver ownership.

## Dependencies
Consumers need `psoc_global_conf_regs.h`, Gaudi2 boot/reset/CoreSight/security code, Linux bitfield helpers, and firmware protocols that assign meaning to scratchpad and message registers. Some fields are shared by firmware and kernel driver, so semantic compatibility matters beyond compile-time correctness.

## Integration Points
Gaudi2 device code uses these masks for boot status, firmware load handoff, reset sequencing, BTM FSM checks, RAZWI diagnostics, and trace/MMU setup. CoreSight uses trace address and AXUSER fields. Security code treats PSOC global configuration ranges specially, including scratchpad access checks.

## Risks
This is a high-blast-radius register block. Incorrect masks can break boot, reset, firmware communication, trace capture, interrupt reporting, isolation, or pad configuration. Reset-persistent registers are especially risky because stale or misdecoded bits can survive across flows. Shared firmware/KMD fields must not be repurposed without protocol coordination.

## Test Signals
Signals include successful cold/warm boot, firmware-load and KMD message exchange, reset/restart sequencing, accurate boot/reset-source reporting, RAZWI diagnostic correctness, CoreSight trace setup, scratchpad/security access validation, interrupt mask/clear behavior, and regression checks against generated hardware specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/psoc_global_conf_masks.h -->
