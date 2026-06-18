# sources/distributed-fs/ceph-client/arch/sparc/kernel/idprom.c

## Purpose
`idprom.c` reads and validates the SPARC IDPROM, exposes the platform MAC address, and prints machine-type information on sparc32.

## Important APIs, Types, and Functions
Global `struct idprom *idprom` is exported. Functions are `arch_get_platform_mac_address()`, `idprom_init()`, internal `calc_idprom_cksum()`, and sparc32 `display_system_type()`.

## Control Flow and State
`idprom_init()` asks PROM to copy the IDPROM into `idprom_buffer`, points `idprom` at it, warns on unknown format or checksum mismatch, displays machine type, and logs Ethernet address. The checksum is XOR over bytes 0 through 0x0e. On sparc32, `display_system_type()` matches `id_machtype` against known Sun/LEON machine constants or queries `banner-name` for OBP sun4m systems.

## Persistence and Dependencies
Persistent state is the static `idprom_buffer` and exported `idprom` pointer. Dependencies include PROM IDPROM APIs, machine constants, and Ethernet address formatting.

## Integration Points, Risks, and Test Signals
Integration includes network default MAC address selection and platform identification. Risks are mostly diagnostic: checksum failure does not stop boot, unknown machine types only warn, and callers assume `idprom_init()` has run before requesting MAC address. Test signals are valid Ethernet address log, correct `TYPE:` log on sparc32, and warning behavior for corrupted IDPROM fixtures.
