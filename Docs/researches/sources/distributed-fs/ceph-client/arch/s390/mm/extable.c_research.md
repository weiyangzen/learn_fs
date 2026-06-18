## sources/distributed-fs/ceph-client/arch/s390/mm/extable.c

Purpose: implements s390 exception table lookup and fixup dispatch. It handles normal kernel exception tables, the special amode31 table, user-access fixups, BPF probe fixups, floating-point-control cleanup, zeropad partial loads, and MVCOS retry behavior.

Important APIs, types, and functions: `s390_search_extables()` searches normal tables first and then `__start_amode31_ex_table` to `__stop_amode31_ex_table`. `fixup_exception()` is the exported dispatcher used by fault handling. Handler helpers include `ex_handler_fixup()`, `ex_handler_ua_fault()`, `ex_handler_ua_load_reg()`, `ex_handler_zeropad()`, `ex_handler_fpc()`, and `ex_handler_ua_mvcos()`. `struct insn_ssf` decodes MVCOS SSF-format operands from the fixup instruction.

Control flow: fault handling calls `fixup_exception()` with pt_regs. If no table entry matches the current instruction pointer, it returns false. Otherwise it switches on `ex->type`, adjusts `regs->psw.addr` to `extable_fixup(ex)`, and edits registers according to the fixup contract. MVCOS faults are retried by trimming the length register to the first page boundary or to zero, ensuring a follow-up instruction completes with condition code zero.

State and persistence: no persistent state is owned here. The only state changes are in `pt_regs`: PSW address, error registers set to `-EFAULT`, zeroed destination registers, data register for zeropad, and FPC reset through `fpu_sfpc(0)`.

Dependencies and integration points: depends on Linux extable helpers, s390 `asm-extable` data encoding, `ex_handler_bpf()` from the BPF JIT, s390 FPU helpers, and `fault.c` kernel fault recovery. It is tightly coupled to assembly annotations that encode `EX_DATA_REG_ADDR`, `EX_DATA_REG_ERR`, and exception type values.

Risks: register metadata in exception table entries must match the faulting instruction; a mismatch can corrupt pt_regs and return to unsafe code. `ex_handler_zeropad()` dereferences an aligned kernel address after a faulting access, so its use must be limited to annotated sequences where that recovery is valid. Unknown exception types deliberately panic.

Test signals: user access helpers should return `-EFAULT` or zeroed data instead of oopsing. BPF probe-memory tests should recover through `EX_TYPE_BPF`. MVCOS boundary tests should show partial-copy progress. Kernel fault tests should verify that unannotated faults still oops.
