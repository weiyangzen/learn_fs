# sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.h

## Purpose
This header defines AT91 SoC identification table structures and constants used by `soc.c`.

## Important APIs, Types, And Functions
`struct at91_soc` contains CIDR match/mask, version mask, EXID match, name, and family. `AT91_SOC()` builds table entries. The header declares `at91_soc_init()` and defines CIDR/EXID constants for many AT91, SAMA5, SAMA7, SAM9X, SAME/SAMS/SAMV devices.

## Control Flow
There is no runtime flow in the header. Constants feed the table scan in `soc.c`, where CIDR and EXID values select a matching SoC descriptor.

## State, Persistence, And Dependencies
The header has no persistent state. It depends on `linux/sys_soc.h` for `struct soc_device`.

## Integration Points
Used by Atmel SoC identification code and potentially other AT91 code that wants the init declaration.

## Risks
Identity constants are hardware facts; typos can cause wrong soc_bus names. The macro positional arguments make mistakes easy, especially because masks and matches are both `u32`.

## Test Signals
Compile `soc.c`, verify every table entry maps to the intended CIDR/EXID, and compare constants with datasheets or known boot logs.
