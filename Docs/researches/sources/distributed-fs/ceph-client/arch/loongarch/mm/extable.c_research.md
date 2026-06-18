<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c

### Purpose
`extable.c` implements LoongArch exception-table fixups for kernel faults, including ordinary fixup jumps, uaccess error/zero fixups, and BPF JIT fixups.

### Important APIs, Types, And Functions
The exported runtime API is `fixup_exception(struct pt_regs *regs)`. Helpers include `get_ex_fixup()`, `regs_set_gpr()`, `ex_handler_fixup()`, and `ex_handler_uaccess_err_zero()`. It consumes `struct exception_table_entry` fields `insn`, `fixup`, `type`, and `data`, plus `EX_TYPE_FIXUP`, `EX_TYPE_UACCESS_ERR_ZERO`, and `EX_TYPE_BPF`.

### Control Flow
On a kernel exception, `fixup_exception()` searches exception tables using `exception_era(regs)`. A normal fixup sets `regs->csr_era` to the relative fixup target. A uaccess fixup extracts error and zero register numbers from `ex->data`, writes `-EFAULT` and `0` into those saved GPR slots, then redirects execution. BPF entries delegate to `ex_handler_bpf()`.

### State, Persistence, And Dependencies
State changes are limited to the interrupted `pt_regs`; no persistent storage exists. Dependencies include generic exception-table search, LoongArch saved-register layout, bitfield helpers, uaccess error conventions, and `asm/asm-extable.h` type/data encoding.

### Integration Points
Fault handling calls this through `no_context()` in `fault.c`. BPF probe-memory loads and stores add extable entries in `net/bpf_jit.c`, and those entries are resolved here via `EX_TYPE_BPF`.

### Risks
Register-offset encoding must match `struct pt_regs`; otherwise fault recovery corrupts state. Relative fixup calculations must stay in range and compatible with sorted exception tables. Unknown types hit `BUG()`, so type drift between assembler/JIT emitters and this dispatcher is fatal.

### Test Signals
Run uaccess fault tests, BPF probe-memory selftests, kernel fault-injection around copy helpers, and cross-build checks for exception-table encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/mm/extable.c -->
