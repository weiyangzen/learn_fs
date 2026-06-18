# sources/distributed-fs/ceph-client/drivers/rapidio/switches/Kconfig

## Purpose
Defines Kconfig symbols for optional RapidIO switch-family drivers under the RapidIO subsystem.

## Important APIs, types, and functions
Symbols are `RAPIDIO_CPS_XX` for IDT CPS-16/12/10/8 Gen1 switches, `RAPIDIO_CPS_GEN2` for IDT CPS Gen2 switches, and `RAPIDIO_RXS_GEN3` for IDT RXS Gen3 switches. All are `tristate`, allowing built-in, module, or disabled builds.

## Control flow
Kconfig has no runtime control flow. The selected symbols drive object inclusion through the sibling Makefile and decide whether the corresponding `rio_driver` registration code is compiled.

## State and persistence
No runtime state. The configuration persists in the kernel `.config`.

## Dependencies and integration
This file is normally sourced from a higher-level RapidIO Kconfig. The symbols integrate with `drivers/rapidio/switches/Makefile`.

## Risks
The help text contains vendor/product spelling issues (`ITD`) but no functional risk. There are no explicit `depends on RAPIDIO` guards here, so correct sourcing context matters.

## Test signals
Build matrix for each symbol as module and built-in; confirm only the expected object is compiled and the switch driver registers.
