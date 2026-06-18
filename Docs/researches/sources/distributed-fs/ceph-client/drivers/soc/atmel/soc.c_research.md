# sources/distributed-fs/ceph-client/drivers/soc/atmel/soc.c

## Purpose
This file identifies Atmel/Microchip AT91-family SoCs from CIDR/EXID registers and registers a soc_bus device.

## Important APIs, Types, And Functions
The `socs[]` table, built conditionally by SoC family config symbols, maps CIDR masks, version masks, EXID values, names, and families. `at91_get_cidr_exid_from_dbgu()` reads legacy DBGU ID registers. `at91_get_cidr_exid_from_chipid()` reads newer chipid nodes. `at91_soc_init()` performs matching and registration. `atmel_soc_device_init()` gates registration to allowed root compatibles.

## Control Flow
At subsys init, the root node is checked against allowed AT91/Microchip compatibles. The code first tries legacy DBGU, then chipid nodes. It scans `socs[]` for a CIDR mask match and, when CIDR indicates extended ID, an EXID match. On success it allocates attributes, formats revision from the configured version mask, registers the soc device, and logs family/name/revision.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated revision string. Dependencies include OF, MMIO mapping, conditional compile symbols for SoC families, and `SOC_BUS`.

## Integration Points
This provides userspace and kernel soc_bus identity for AT91RM9200, AT91SAM9, SAM9X60, SAM9X7, SAMA5, SAMV7, SAMA7D6, and SAMA7G5 variants.

## Risks
The table is large and conditionally compiled, so missing config coverage can make a supported SoC unidentifiable. Some SAM9X7 entries appear to pass EXID values as CIDR masks, which should be checked against intended matching semantics. Failure returns NULL rather than detailed errno from `at91_soc_init()`.

## Test Signals
Boot every supported family, verify soc_bus attributes and revision masks, test legacy DBGU and chipid paths, unknown CIDR/EXID fallback, and configuration combinations that include/exclude table blocks.
