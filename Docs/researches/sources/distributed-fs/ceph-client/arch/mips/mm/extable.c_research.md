# sources/distributed-fs/ceph-client/arch/mips/mm/extable.c

Purpose: MIPS exception table fixup helper for recoverable kernel faults.

Important APIs/functions: `fixup_exception(struct pt_regs *regs)` searches exception tables using `exception_epc(regs)`. If a fixup is found, it rewrites `regs->cp0_epc` to `fixup->nextinsn` and returns true.

Control flow: simple lookup and branch. No locks or allocations are taken, making it suitable for page fault/oops recovery contexts.

State and persistence: mutates only the register frame EPC passed by the caller.

Dependencies and integration: used by `fault.c` in the kernel no-context page fault path. Depends on Linux extable infrastructure and MIPS branch-aware `exception_epc()`.

Risks and test signals: correctness depends on the EPC used for branch-delay exceptions. Test recoverable copy_to/from_user faults, branch-delay fault fixups, and no-fixup kernel oops behavior.
