# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_acpi_sar.h

## Purpose
This header defines the packed ACPI SAR table layouts and constants used by the MT792x ACPI SAR parser.

## Important APIs, Types, And Functions
It defines min/max counts for dynamic/geographic/flag tables, ACPI method names `MTCL`, `MTDS`, `MTGS`, `MTFG`, invalid MTCL sentinel, and packed structures for dynamic SAR v1/v2, geographic SAR v1/v2, country-list v1/v3, flag tables, and the aggregate `mt792x_acpi_sar` container. There are no functions.

## Control Flow
The parser in `mt792x_acpi_sar.c` casts ACPI byte packages to these structures after validating package length. Version fields select which union view is valid and which flexible array record sizes are used.

## State And Persistence
Instances are allocated with devm lifetime and stored in `phy->acpisar`. The flexible arrays hold platform-provided regulatory and power-limit tables; they are treated as immutable after initialization.

## Dependencies And Integration Points
The header is included by `mt792x.h` and therefore visible to MT792x driver files. It relies on Linux bitfield/flexible-array conventions through included kernel headers.

## Risks
Packed layout and flexible arrays must match ACPI firmware exactly. The include guard name still says `MT7921`, which is cosmetic but could confuse maintenance. Adding table versions requires updating both this header and parser validation.

## Test Signals
Compilation under `CONFIG_ACPI`, correct parsing of v1/v2/v3 ACPI method payloads, and SAR/MTCL behavior on real platform firmware validate this contract.
