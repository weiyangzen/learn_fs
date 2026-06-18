# sources/distributed-fs/ceph-client/arch/m68k/mac/oss.c

## Purpose
Handles the IIfx Operating System Services chip, which replaces VIA2 and provides programmable interrupt levels.

## APIs, Flow, And State
Global state is `int oss_present` and `volatile struct mac_oss *oss`. `oss_init()` detects `MAC_MODEL_IIFX`, maps `OSS_BASE`, marks OSS present, and disables all interrupt sources by setting their level to zero. `oss_register_interrupts()` chains autovectors for ISM IOP, SCSI, NuBus, SCC IOP, and VIA1, then enables the VIA1 source. Handler functions translate OSS source events into Mac IRQs, including NuBus pending-bit fan-out. `oss_irq_enable()` and `oss_irq_disable()` map Mac IRQs to OSS source level registers, with VIA1 delegated to VIA routines.

## Dependencies And Integration
Depends on `asm/mac_oss.h`, VIA1 interrupt handling, Mac IRQ encodings, and `macintosh_config`. It integrates with `macints.c`, `iop.c`, and IIfx SCSI/SCC/ADB behavior.

## Risks And Test Signals
The file notes uncertainty about clearing pending OSS IRQs. Wrong level mapping can block IIfx ADB, SCSI, SCC, or NuBus. Test signals are IIfx boot IRQ routing, working ISM/SCC IOP interrupts, SCSI interrupts, NuBus slot dispatch, and poweroff via `oss->rom_ctrl`.
