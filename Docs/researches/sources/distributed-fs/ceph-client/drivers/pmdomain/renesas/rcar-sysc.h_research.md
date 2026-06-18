<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h

## Purpose
Shared header for legacy R-Car/RZ SYSC descriptor files and `rcar-sysc.c`. It defines descriptor structures, domain flag semantics, and extern declarations for all legacy SoC `*_sysc_info` objects.

## Important APIs, Types, And Functions
Defines `PD_CPU`, `PD_SCU`, `PD_NO_CR`, `PD_OFF_DELAY`, aliases `PD_CPU_CR`, `PD_CPU_NOCR`, `PD_ALWAYS_ON`, `struct rcar_sysc_area`, and `struct rcar_sysc_info`. No functions are implemented.

## Control Flow
Compile-time only. Descriptor files populate `rcar_sysc_area` arrays; `rcar-sysc.c` uses the `rcar_sysc_info` objects selected by OF compatible and Kconfig.

## State And Persistence Behavior
No runtime state. It describes init-time data consumed by the framework.

## Dependencies And Integration Points
Depends on Linux integer types and `BIT()` availability through included kernel headers in users. It is the contract between per-SoC descriptor objects and the legacy SYSC framework.

## Risks
Flag macro changes affect every descriptor. Extern declarations must match object constness: `r8a7795_sysc_info` is non-const because revision fixups mutate it.

## Test Signals
All Renesas legacy descriptor files should compile with this header, and the framework should link all enabled externs. Static review should confirm new SoCs use the correct flags and parent/isr indexing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-sysc.h -->
