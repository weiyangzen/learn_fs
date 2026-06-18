<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h

## Purpose
This header defines UltraSPARC Cheetah/Cheetah+/Jalapeno asynchronous fault status register bits.

## Important APIs, Types, and Functions
It defines sticky error bits such as `CHAFSR_PERR`, `CHAFSR_IERR`, `CHAFSR_UE`, `CHAFSR_CE`, Cheetah+ additions, Jalapeno-specific `JPAFSR_*` fields, syndrome masks/shifts, and aggregate masks `CHAFSR_ERRORS`, `CHPAFSR_ERRORS`, and `JPAFSR_ERRORS`.

## Control Flow
Trap and error-handling code reads AFSR/AFAR, masks with these definitions, reports error classes, and writes one bits back to clear sticky status before re-enabling interrupts.

## State and Persistence Behavior
State is in CPU fault-status registers. Bits are sticky and must be explicitly cleared; syndrome/address capture remains frozen until the corresponding logged bit is cleared.

## Dependencies and Integration Points
It integrates with SPARC64 trap handlers, EDAC/memory-controller diagnostics, machine check reporting, and platform-specific CPU error code.

## Risks
Clearing the wrong bit can lose diagnostic evidence or unlock AFAR/syndrome capture too early. Failing to clear disrupting-trap bits can retrigger the same trap.

## Test Signals
Use fault injection or platform error logs, verify decoded error names/syndromes, and confirm handlers clear AFSR without repeated traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/chafsr.h -->
