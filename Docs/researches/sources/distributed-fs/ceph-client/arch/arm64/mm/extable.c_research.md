# sources/distributed-fs/ceph-client/arch/arm64/mm/extable.c

Purpose: handles ARM64 exception table fixups for uaccess, BPF, kernel access zeroing, copy faults, and unaligned zeropad loads.

Important APIs/types/functions: `cpy_faulted_on_uaccess`, `insn_may_access_user`, `get_ex_fixup`, `ex_handler_uaccess_err_zero`, `ex_handler_uaccess_cpy`, `ex_handler_load_unaligned_zeropad`, and `fixup_exception`.

Control flow: `fixup_exception` looks up the faulting instruction in exception tables, dispatches by type, updates registers and PC to the fixup target, and returns whether the exception was handled. Copy fixups validate ESR write/read direction so kernel-side faults are not hidden as user faults. Unaligned zeropad reads the aligned word, shifts based on endian offset, writes the result register, and resumes at fixup.

State and persistence: mutates transient `pt_regs` and possibly register values. No persistent state.

Dependencies/integration: fault handler calls, exception table encoding from `asm-extable.h`, BPF exception handler, uaccess assembly, ESR fields, and ARM64 register access helpers.

Risks: incorrect exception type metadata can hide real kernel faults or fail valid uaccess recovery. `LOAD_UNALIGNED_ZEROPAD` dereferences an aligned kernel word during fixup and relies on surrounding extable assumptions. Unknown extable types `BUG()`.

Test signals: uaccess copy/read/write faults, kernel access err-zero fixups, BPF probe fault recovery, zeropad unaligned loads across page ends, ESR WnR direction mismatch, and fault-injection into annotated assembly.
