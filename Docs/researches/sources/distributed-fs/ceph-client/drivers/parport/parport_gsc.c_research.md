# sources/distributed-fs/ceph-client/drivers/parport/parport_gsc.c

## Purpose
`parport_gsc.c` is the HP PA-RISC GSC/LASI low-level parallel-port driver for PC-style hardware. It probes SPP and bidirectional capability, registers a parport instance, handles IRQ setup, and binds to PA-RISC FIO devices.

## Important APIs, Types, and Functions
`parport_gsc_ops` is the operation table, with basic accessors from `parport_gsc.h` and generic IEEE 1284 fallbacks. `clear_epp_timeout()`, `parport_SPP_supported()`, and `parport_PS2_supported()` probe hardware behavior. `parport_gsc_probe_port()` allocates private data and copied ops, performs detection, registers the port, requests IRQ if available, initializes data direction, and announces the port. `parport_init_chip()` is the PA-RISC probe entry.

## Control Flow
The PA-RISC driver matches HPHW_FIO sversion `0x74`. Probe checks a platform IRQ, computes port base as HPA plus `PARPORT_GSC_OFFSET`, optionally initializes enhanced mode on newer CPUs with valid PDC address, then probes the port. Port probing first tests a stack `struct parport` for hardware existence, then registers a real parport and transfers detected modes. Removal unregisters, frees IRQ, frees private data and copied ops, and drops the parport reference.

## State and Persistence
`struct parport_gsc_private` stores cached control register value, writable control mask, PWord metadata placeholders, and unused DMA-related fields. Driver-global `parport_count` counts successful probes. Hardware state is in GSC memory-mapped data/status/control registers.

## Dependencies and Integration Points
The driver depends on PA-RISC device registration, PDC address validation, SuperIO/GSC I/O helpers, parport core, and generic IEEE 1284 software operations. `parport_gsc.h` supplies inline register access and control-bit handling.

## Risks
`parport_count` is incremented but not used for policy. EPP/ECP advanced detection is limited; modes printed exclude ECP/DMA. The copied ops table is freed on removal with a comment noting risk if someone cached it. Probe manually allocates before `parport_register_port()`, so all failure paths must keep private and ops lifetimes paired.

## Test Signals
Boot on LASI/GSC systems should log the PC-style base, IRQ, and modes. Hardware tests should verify SPP data read/write, PS/2 tristate detection, IRQ fallback to polled operation when busy, and clean driver unregistration.
