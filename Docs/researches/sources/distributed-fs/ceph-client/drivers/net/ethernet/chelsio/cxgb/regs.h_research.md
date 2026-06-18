# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/regs.h

## Purpose
`regs.h` is the main ASIC register map for the Chelsio cxgb T1/T2 driver. It defines MMIO and PCI configuration offsets plus bitfield helpers for SGE DMA, MC3/MC4 memory controllers, TPI, TP offload engine, RAT routing, CSPI/ESPI, ULP, PL interrupt routing, MC5 TCAM, and PCI/PCI-X configuration.

## Important APIs, Types, and Functions
The file exports no functions. Its API is the macro namespace: address macros prefixed `A_`, shift macros `S_`, masks `M_`, value constructors `V_`, getters `G_`, and single-bit flags `F_`. Important blocks include `A_SG_*` for command/free/response queues, doorbells, interrupt timers, and SGE interrupt causes; `A_MC3_*` and `A_MC4_*` for memory timing/ECC/BIST/backdoor access; `A_TPI_*` for indirect external-chip access; `A_TP_*` for TOE/checksum/offload/timer/QoS/MTU/drop configuration; `A_RAT_*` for route table and framing errors; `A_CSPI_*` and `A_ESPI_*` for SPI4 datapaths; `A_ULP_*` for ULP parity/sync errors; `A_PL_ENABLE`/`A_PL_CAUSE` for top-level interrupts; `A_MC5_*` for TCAM and DBGI access; and `A_PCICFG_*` for VPD, PM CSR, interrupt cause, and PCI mode.

## Control Flow
There is no executable flow, but many driver flows are built from these constants. SGE setup writes queue base/size/credit/control registers. Interrupt paths read/write SGE, ESPI, PL, TP, ULP, RAT, MC, and PCI cause/enable registers. Ettool register dump uses ranges from this map. ESPI initialization configures `A_ESPI_*`, T2 TRICN command/status, and monitored-counter fields. PCI reset writes `A_PCICFG_PM_CSR`.

## State and Persistence
The header represents hardware state in adapter registers. Register contents persist while the device is powered and not reset; driver software shadows only selected fields such as SGE control and ESPI misc control. The header itself has no memory or persistence.

## Dependencies and Integration Points
Nearly every cxgb implementation file includes `regs.h`: `cxgb2.c` for register dumps/reset, `sge.c` for DMA and interrupt registers, `espi.c` for ESPI programming, `pm3393.c` for PL external interrupt routing, and common initialization/interrupt modules for memory/TP/RAT/MC5/PCI handling. It is the common contract between software and T1/T2 hardware documentation.

## Risks
This file is high blast-radius: wrong constants can corrupt DMA rings, mask fatal interrupts, misconfigure memory controllers, or break offload behavior. Similar field names appear in multiple blocks, so callers must use the correct address and bit namespace. Some registers have write-one-to-clear semantics, some are read-clear, and some require timing/polling; the macros do not encode those semantics. Endianness and register width assumptions must match MMIO accessors in callers.

## Test Signals
Signals include successful hardware initialization, ethtool register dump ranges returning sane values, SGE TX/RX traffic, interrupt enable/clear for SGE/ESPI/PL/TP/MC/PCI errors, TPI external-chip access, TP checksum offload, ESPI monitor reads, PCI VPD/PM reset behavior, and no regressions across T1B/T2 and FPGA/ASIC board variants after changing any register definition.
