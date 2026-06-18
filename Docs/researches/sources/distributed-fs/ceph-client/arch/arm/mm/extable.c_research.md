## sources/distributed-fs/ceph-client/arch/arm/mm/extable.c

### Purpose
Provides ARM exception-table fixup handling for recoverable kernel faults, especially uaccess and nofault probes.

### Important APIs, Types, And Functions
The single exported architecture hook is `fixup_exception(struct pt_regs *regs)`. It calls `search_exception_tables(instruction_pointer(regs))`, sets `regs->ARM_pc` to the fixup target, and clears Thumb-2 IT state when needed.

### Control Flow
On a kernel fault, fault handling asks this helper whether the current PC has a fixup entry. If yes, execution resumes at the fixup address and the fault is considered handled; otherwise normal oops processing continues.

### State, Dependencies, And Integration
No local persistent state. Depends on generic exception table lookup, `pt_regs`, uaccess, and Thumb-2 CPSR definitions. Integrated by `fault.c` in `__do_kernel_fault`.

### Risks And Test Signals
Risks are incorrect PC rewrite, missing IT-state clearing for Thumb-2, or broken exception table generation. Test uaccess fault recovery, `copy_from_kernel_nofault`, probe_kernel_read-style users, and Thumb-2 kernel builds.
