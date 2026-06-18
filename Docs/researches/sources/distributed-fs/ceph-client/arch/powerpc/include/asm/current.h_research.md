## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/current.h

Purpose: provides the architecture implementation of the `current` task pointer.

Important APIs/types/functions: on PPC64, `get_current()` loads `paca->__current` from r13-relative PACA storage and `#define current get_current()`. On 32-bit, `current` is a global register variable in r2.

Control flow: PPC64 emits a single load from PACA offset; PPC32 uses compiler-reserved register state.

State and persistence: reads task pointer state maintained by context-switch code in PACA or r2. The header does not mutate it.

Dependencies and integration: depends on PACA layout offsets, `struct task_struct`, and compiler register allocation rules. Used by virtually all kernel code that references `current`.

Risks and test signals: wrong PACA offset or register convention breaks every task-context access. Test signals include early boot, context switching, preemption, modules compiled with this header, and mkdefs/offsetof consistency checks.
