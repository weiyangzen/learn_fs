<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h

## Purpose
This header exposes SPARC EEPROM/NVRAM interfaces.

## Important APIs, Types, and Functions
It declares constants or functions used to access firmware-stored EEPROM data.

## Control Flow
Platform or char-device code includes it when reading/writing EEPROM-backed configuration.

## State and Persistence Behavior
State persists in EEPROM/NVRAM hardware, not in the header.

## Dependencies and Integration Points
It integrates with OpenPROM/NVRAM drivers and platform identity/configuration code.

## Risks
Writes can persist across reboots; incorrect offsets may corrupt firmware settings.

## Test Signals
Read EEPROM contents, compare with PROM tools, and test write paths only on disposable hardware/configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/eeprom.h -->
