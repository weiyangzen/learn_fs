<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig

## Purpose
Highlander board revision selector under SH_HIGHLANDER. It chooses one of R7780RP, R7780MP, or R7785RP and constrains each to the matching SH7780/SH7785 CPU subtype, with R7785RP selecting GPIOLIB.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_R7780RP, SH_R7780MP, SH_R7785RP.
- Source-tree integration: mach-highlander; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-highlander/Kconfig -->
