# sources/distributed-fs/ceph-client/drivers/gpib/include/tnt4882_registers.h

## Purpose

`tnt4882_registers.h` defines register offsets, status/control bits, FIFO/DMA control bits, and auxiliary commands for National Instruments TNT4882/Turbo-488 style controllers.

## Important APIs and Constants

- Register offsets include 9914-mode auxiliary registers, handshake/configuration registers, counters, FIFOs, command register, timer, status registers, interrupt registers, and bus control/status.
- `tnt_pagein_offset` identifies the alternate-register page-in offset.
- Bus status bits mirror REN, IFC, SRQ, EOI, NRFD, NDAC, DAV, and ATN.
- `enum cfg_bits`, `enum cmdr_bits`, `enum hssel_bits`, `enum imr0_bits`, `enum isr0_bits`, `enum isr3_bits`, `enum keyreg_bits`, `enum sts1_bits`, and `enum sts2_bits` describe FIFO, transfer, interrupt, delay, DMA, and status behavior.
- `enum tnt4882_aux_cmds` includes mode switching, request-service control, page-in, immediate holdoff, clear-END, and 7210/9914 mode commands.
- Auxiliary register bit enums provide no-talking-without-listeners, local parallel poll, holdoff, static interrupt, PP2, and ultra-short T1 settings.

## Control Flow and Integration

This header is a hardware vocabulary for TNT4882-aware code. It is not directly used by the implementation files in this subset, but it complements the NEC/TMS controller headers for other GPIB board drivers.

## State and Persistence Behavior

No in-memory state is declared. State is in hardware registers and any driver-side shadows maintained by users of these constants.

## Dependencies

The header is self-contained and guarded.

## Risks and Test Signals

Many constants share common names with other register headers (`AUXCR`, `IMR0`, `ISR0`), so inclusion ordering and translation-unit scope matter. Test signals are TNT hardware initialization, FIFO reset/start/stop, interrupt decode, mode switching between 9914/7210, T1 delay setting, and bus-status readback.
