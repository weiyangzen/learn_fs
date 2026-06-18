<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig

## Purpose
Migo-R LCD-panel selector, choosing between QVGA and RTA WVGA panel configurations under SH_MIGOR.

## Important APIs, Types, and Functions
- no callable C entry points; behavior is selected through Kconfig/Kbuild metadata.

## Control Flow
- The menu is evaluated at configuration time; selected symbols control which board objects compile and which device paths are enabled.

## State and Persistence
- no durable software state beyond compile-time selection and static constants.

## Dependencies and Integration Points
- Kconfig symbols: SH_MIGOR_QVGA, SH_MIGOR_RTA_WVGA.
- Source-tree integration: mach-migor; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- main risk is stale board metadata silently excluding or including the wrong object for a configuration.

## Test Signals
- configuration tests should verify valid symbol visibility for matching CPU subtypes and one selected board option.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-migor/Kconfig -->
