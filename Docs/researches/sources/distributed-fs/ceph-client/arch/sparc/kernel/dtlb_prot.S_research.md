# sources/distributed-fs/ceph-client/arch/sparc/kernel/dtlb_prot.S

## Purpose
`dtlb_prot.S` is a sparc64 trap-table fragment for data TLB protection faults, mainly writes to read-only pages from user mode, nucleus-to-user accesses, and higher-trap-level stack-frame faults.

## Important APIs, Types, and Functions
It has no exported callable functions. It uses `TLB_SFSR`, `TLB_TAG_ACCESS`, `ASI_DMMU`, `PSTATE_AG`, `PSTATE_MG`, `FAULT_CODE_DTLB`, `FAULT_CODE_WRITE`, and external labels `winfix_trampoline` and `sparc64_realfault_common`.

## Control Flow and State
The fragment clears the DMMU fault-valid bit, switches to alternate globals, checks the trap level, reads tag-access to recover the faulting virtual address without context bits, and builds a DTLB-write fault code. For trap levels above one it branches to window-fixup before real fault processing; otherwise it enters `sparc64_realfault_common`.

## Persistence and Dependencies
It mutates DMMU fault state and processor global register state during trap handling. It depends on V9 trap-level semantics, window-fixup code, and the generic sparc64 fault path.

## Integration Points, Risks, and Test Signals
Integration is with the trap table, winfixup, and memory fault handlers. Risks are high because this path runs before normal C state exists; incorrect fault address extraction or trap-level routing can corrupt user windows or panic on copy-to-user faults. Test signals include copy-on-write behavior, user write-protect faults, kernel user-access fault recovery, and no recursive TL>1 trap loops.
