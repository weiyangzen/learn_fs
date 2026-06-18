## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-uaccess.h

### Purpose
Defines ARM64 assembly macros for enabling/disabling user access and annotating user memory loads/stores with exception table fixups.

### Important APIs, Types, And Functions
Important macros are `__uaccess_ttbr0_disable`, `__uaccess_ttbr0_enable`, `uaccess_ttbr0_disable`, `uaccess_ttbr0_enable`, `USER`, `USER_CPY`, `user_ldp`, `user_stp`, and `user_ldst`.

### Control Flow
When software TTBR0 PAN is enabled and hardware PAN is unavailable, macros save DAIF, switch TTBR0 to reserved page tables or restore task TTBR0/ASID, and then restore interrupts. `USER*` macros wrap faulting instructions and emit exception table records. Pair/unprivileged load/store helpers expand to LDTR/STTR sequences with fixups for each instruction.

### State, Persistence, And Dependencies
State affected is TTBR0_EL1, TTBR1_EL1 ASID bits, DAIF interrupt mask, and exception table metadata. Dependencies include alternatives, extable macros, assembler helpers, kernel page table constants, MMU constants, and sysreg definitions.

### Integration Points
Used by ARM64 usercopy, signal, access_ok-adjacent assembly, and low-level routines that temporarily permit user address translation.

### Risks
TTBR/ASID switching must be interrupt-safe and ordered by ISB. Missing exception table entries can turn user faults into kernel faults. Hardware PAN alternatives must patch to no-ops correctly.

### Test Signals
Run usercopy fault tests, PAN/SW_TTBR0_PAN boot variants, KASAN invalid user pointer tests, signal frame access tests, and objdump checks for exception table entries around LDTR/STTR sequences.
