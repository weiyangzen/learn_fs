<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h

## Purpose
`processor_32.h` defines 32-bit UML thread architecture state, including TLS descriptors and debug registers.

## Important APIs, types, and functions
Types/macros include `struct uml_tls_struct`, `struct arch_thread`, `INIT_ARCH_THREAD`, `STACKSLOTS_PER_LINE`, `arch_flush_thread()`, `arch_copy_thread()`, `current_sp()`, and `current_bp()`.

## Control flow
Fork/exec/thread cleanup copies or clears TLS arrays; ptrace/sysrq code uses debug register and saved fault info fields.

## State and persistence behavior
Persistent per-task state includes three TLS descriptors with present/flushed bits, eight debug registers, a sequence number, and last fault info.

## Dependencies and integration points
It depends on `asm/segment.h`, `asm/ldt.h`, and 32-bit TLS management in `tls_32.c`.

## Risks and edge cases
TLS flush bookkeeping must stay synchronized with host thread-area state; stale descriptors can leak into another UML task.

## Test signals
Signals are 32-bit clone/set_thread_area, context-switch TLS tests, and ptrace debug-register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_32.h -->
