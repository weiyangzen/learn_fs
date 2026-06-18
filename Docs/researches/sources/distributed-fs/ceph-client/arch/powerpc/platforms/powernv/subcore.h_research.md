## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.h

### Purpose
`subcore.h` defines synchronization constants and declarations shared by the C and assembly subcore split implementation.

### Important APIs, Types, And Functions
The ordered constants are `SYNC_STEP_INITIAL`, `SYNC_STEP_UNSPLIT`, `SYNC_STEP_REAL_MODE`, and `SYNC_STEP_FINISHED`. Under SMP it declares `split_core_secondary_loop()` and `update_subcore_sibling_mask()`; non-SMP gets an empty inline for sibling-mask updates.

### Control Flow
The constants are compared with `<=`/`<` style waits in `subcore.c` and are written directly by the assembly helper.

### State, Persistence, And Dependencies
The header has no storage of its own. It depends on being included consistently by C and assembler and on the constant ordering remaining monotonic.

### Integration Points
It bridges `subcore.c` and `subcore-asm.S`.

### Risks
Changing numeric order would break synchronization waits. Missing declarations under config combinations would break builds.

### Test Signals
SMP and non-SMP compile coverage plus split-mode runtime tests validate this header.
