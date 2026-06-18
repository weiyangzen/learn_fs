<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h

### Purpose
`unaligned.h` declares the local PA-RISC unaligned-access handler interface.

### Important APIs, Types, And Functions
It forward-declares `struct pt_regs` and declares `handle_unaligned()` and `check_unaligned()`.

### Control Flow
No runtime control flow is present; it allows trap code to call the unaligned implementation without exposing internals.

### State, Persistence, And Dependencies
No state is defined. The declarations depend only on `struct pt_regs`.

### Integration Points
Included by `traps.c` and implemented by `unaligned.c`.

### Risks
The header is intentionally tiny; signature mismatches would be caught at compile time.

### Test Signals
Build coverage of `traps.c` plus runtime unaligned trap tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/unaligned.h -->
