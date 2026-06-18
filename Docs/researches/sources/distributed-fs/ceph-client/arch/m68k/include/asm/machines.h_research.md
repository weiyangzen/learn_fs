<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h

## Purpose
`machines.h` defines Sun machine-type decoding constants used with IDPROM machine identifiers.

## Important APIs, Types, and Functions
It defines `struct Sun_Machine_Models`, `NUM_SUN_MACHINES`, architecture masks and values (`SM_SUN3`, `SM_SUN3X`, etc.), type masks, and model IDs for Sun3, Sun3x, and legacy Sun4/Sun4c/Sun4m classes.

## Control Flow, State, and Persistence
There is no runtime code. Constants decode the `id_machtype` byte read from IDPROM.

## Dependencies and Integration Points
Sun3 IDPROM code and model reporting use these constants. The header is adapted from broader SPARC definitions but reduced for the m68k Sun3 port.

## Risks
The include guard still uses `_SPARC_MACHINES_H`, which is historically odd but functional. The model count must remain aligned with the model table in `arch/m68k/sun3/idprom.c`.

## Test Signals
Signals include correct decoding of Sun3/160, 3/50, 3/260, 3/110, 3/60, 3/E, 3/460, and 3/80 IDPROM values and matching model-table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/machines.h -->
