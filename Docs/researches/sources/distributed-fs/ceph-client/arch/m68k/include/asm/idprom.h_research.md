<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h

## Purpose
`idprom.h` defines the Sun IDPROM data layout used by m68k Sun3/Sun3x code to identify machine type, Ethernet address, manufacture date, serial number, and checksum.

## Important APIs, Types, and Functions
`struct idprom` models the PROM bytes, including `id_format`, `id_machtype`, `id_ethaddr[6]`, `id_date`, a 24-bit serial field, checksum, and reserved bytes. It declares global `struct idprom *idprom`, `idprom_init()`, and `SUN3_IDPROM_BASE`.

## Control Flow, State, and Persistence
The PROM contents are read once by `idprom_init()` and then persisted through the global pointer for machine setup and network address users.

## Dependencies and Integration Points
It depends on Linux integer types and Sun machine definitions. Ethernet drivers and Sun3 platform setup use the parsed identity data.

## Risks
The bitfield serial representation is compiler-layout-sensitive, although the surrounding m68k ABI is fixed. Checksum validation is outside this header. Consumers must not dereference `idprom` before initialization.

## Test Signals
Boot logs should report correct Sun3/Sun3x model and MAC address. Tests or instrumentation should verify checksum handling and that `id_machtype` maps correctly through `machines.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/idprom.h -->
