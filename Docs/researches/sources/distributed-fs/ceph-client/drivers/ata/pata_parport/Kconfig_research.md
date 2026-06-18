# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/Kconfig

## Purpose
Defines Kconfig entries for optional parallel-port IDE protocol modules used by the `pata_parport` core.

## Important APIs, Types, And Functions
The file declares tristate options for ATEN, MicroSolutions BACKPACK Series 5 and 6, DataStor, Fidelity, Shuttle, Freecom, KingByte, KT, and OnSpec protocols. `PATA_PARPORT_EPATC8` is a bool child option of `PATA_PARPORT_EPAT` that enables Shuttle EP1284/c7/c8 support.

## Control Flow
There is no runtime control flow. Build-time dependency resolution requires `PATA_PARPORT`, then allows each protocol module to be compiled built-in, modular, or omitted.

## State And Persistence
Configuration state persists in the kernel `.config`; it determines which protocol drivers are compiled and therefore which `pi_protocol` registrations are available at runtime.

## Dependencies And Integration Points
Integrates with `drivers/ata/pata_parport/Makefile`, the central `PATA_PARPORT` option, and individual protocol modules that call `pata_parport_register_driver()`.

## Risks And Edge Cases
Selecting the wrong BACKPACK series or omitting EPATC8 support can make real hardware invisible. Built-in protocol choices affect probing order and may keep some Freecom powered devices enabled for the life of the kernel.

## Test Signals
Kconfig dependency checks, module build matrix for every option, EPAT with and without c8 support, and boot/module-load probing with multiple protocol options enabled.
