# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/flash_setup.c

## Purpose
Maps Octeon bootbus CFI flash into Linux MTD using device-tree discovery and bootbus region configuration.

## Important APIs, Types, And Functions
Functions include `octeon_flash_map_read()`, `octeon_flash_map_write()`, `octeon_flash_map_copy_from()`, `octeon_flash_map_copy_to()`, `octeon_flash_probe()`, and `octeon_flash_init()`. Static state is `flash_map`, `mymtd`, and partition probe list.

## Control Flow
Late init registers an OF platform driver matching `cfi-flash`. Probe reads the chip-select `reg`, reads `CVMX_MIO_BOOT_REG_CFGX`, computes flash base/size/bankwidth, maps it, installs semaphore-protected map ops, probes CFI, and registers partitions.

## State, Persistence, And Dependencies
The MTD map and pointer persist after probe. Accesses are serialized with `octeon_bootbus_sem`. Dependencies include OF, MTD map APIs, CFI probing, and Octeon bootbus CSRs.

## Integration Points
Integrates bootbus flash with Linux MTD and command-line/RedBoot partition parsing. The legacy map name is kept for old partition lines.

## Risks
No remove path or iounmap cleanup. `ioremap()` failure is not checked. Size calculation assumes the bootloader alias layout below `0x1fc00000`.

## Test Signals
Check OF probe, boot log map base/size, successful CFI probe, partition registration, and serialized flash access under bootbus contention.
