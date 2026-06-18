<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig

## Purpose
Defines x86 RAS Correctable Errors Collector options.

## Important APIs, Types, And Functions
`RAS_CEC` enables the correctable error collector and selects `BITREVERSE`. `RAS_CEC_DEBUG` enables debugfs support for CEC and depends on `RAS_CEC`.

## Control Flow
Kconfig presents options and dependency/help text; no runtime code exists here.

## State And Persistence
The selected config controls compiled code and optional debugfs exposure elsewhere.

## Dependencies And Integration Points
Integrates with x86 RAS/MCE code and debugfs when enabled.

## Risks And Edge Cases
Debug support can expose internal state and should remain dependent on the collector. Config help must accurately describe platform support.

## Test Signals
Kconfig dependency resolution, builds with CEC/debug enabled and disabled, and expected debugfs presence under debug config validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/ras/Kconfig -->
