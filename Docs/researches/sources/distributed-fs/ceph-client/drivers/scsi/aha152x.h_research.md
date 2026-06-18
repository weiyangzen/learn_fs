# sources/distributed-fs/ceph-client/drivers/scsi/aha152x.h

## Purpose
`aha152x.h` defines the register map, bit fields, helper macros, autoconfiguration layout, and externally visible setup/probe interfaces for the AHA-152x driver.

## Important APIs, Types, And Functions
The header declares `AHA152X_MAXQUEUE`, `AHA152X_REVID`, port offset macros such as `SCSISEQ`, `SXFRCTL0`, `SCSISIG`, `SCSIRATE`, `SSTAT0`, `SSTAT1`, `SIMODE0`, `DMACNTRL0`, `DMASTAT`, and `DATAPORT`, and constants for SCSI phases, interrupt sources, FIFO/DMA controls, and test registers. `aha152x_config` models PORTA/PORTB board configuration. `struct aha152x_setup` carries configuration into `aha152x_probe_one()`. The public declarations are `aha152x_probe_one()`, `aha152x_release()`, and `aha152x_host_reset_host()`.

## Control Flow
The header has no runtime control flow, but it encodes the control vocabulary used by the driver. The state machine tests `SSTAT0`, `SSTAT1`, `DMASTAT`, and `SCSISIG` bits, acknowledges interrupt conditions through write-to-clear bits, selects SCSI phases via `P_*` masks, enables interrupt sources through `SIMODE0/1`, and changes FIFO/DMA behavior through `SXFRCTL0` and `DMACNTRL0`.

## State And Persistence Behavior
All state described here is volatile hardware state: register bits, transfer counters, FIFO status, message/data phase signals, and configuration latch fields. `aha152x_config` captures firmware/jumper-like configuration exposed through controller ports, but the header itself persists nothing.

## Dependencies And Integration Points
The macros assume `HOSTIOPORT0` and `HOSTIOPORT1` are defined in the including C file and depend on Linux `inb()`/`outb()`. The public setup structure depends on `struct Scsi_Host` from the SCSI mid-layer through declarations only. The header is tightly coupled to `aha152x.c`.

## Risks
The port macros directly evaluate their arguments and perform raw I/O, so misuse can touch incorrect hardware ports. The `aha152x_config` bitfield layout is compiler- and endian-sensitive in principle. Several definitions encode write-to-clear status bits; confusing read status with clear values can lose interrupts.

## Test Signals
Compile coverage is the primary signal. Runtime signals include successful port tests, correct phase decoding in proc diagnostics, valid autodetected IRQ/SCSI ID fields, and correct data transfer behavior when `ENDMA`, `_8BIT`, `WRITE_READ`, `DFIFOEMP`, and `DFIFOFULL` paths are exercised.
