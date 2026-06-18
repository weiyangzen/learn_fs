<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h

## Purpose
Shared header for R-Car Gen4 SYSC descriptors and framework. It defines Gen4 domain flags, the compact PDR-based area descriptor, the SoC info container, and extern declarations for Gen4 SoC tables.

## Important APIs, Types, And Functions
Defines `PD_CPU`, `PD_SCU`, `PD_NO_CR`, `PD_CPU_NOCR`, `PD_ALWAYS_ON`, `struct rcar_gen4_sysc_area`, and `struct rcar_gen4_sysc_info`. No executable functions are present.

## Control Flow
Compile-time descriptor contract only. Gen4 SoC files populate arrays of `rcar_gen4_sysc_area`; `rcar-gen4-sysc.c` turns those arrays into genpd domains.

## State And Persistence Behavior
No runtime state. Data described by this header is init-time descriptor metadata.

## Dependencies And Integration Points
Depends on Linux types and the family framework. Externs must match objects in `r8a779a0/f0/g0/h0-sysc.c` and Makefile/Kconfig inclusion.

## Risks
Incorrect flag semantics affect all Gen4 SoC descriptors. Parent ID semantics differ from legacy channel/isr descriptors, so mixing headers would be a serious integration bug.

## Test Signals
All Gen4 descriptors should compile and link. Boot validation should confirm onecell indices match PDR IDs from dt-bindings.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rcar-gen4-sysc.h -->
