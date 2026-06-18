# sources/distributed-fs/ceph-client/arch/s390/include/asm/processor.h

Purpose: This header defines s390 per-CPU processor metadata, thread state, CPU flags, task address layout, PSW helpers, machine-check mask helpers, stack helpers, and low-level CPU instructions.

Important APIs/types/functions: It exposes CIF flags, `struct pcpu`, per-CPU `pcpu_devices`, CPU-flag bit helpers, `get_cpu_id()`, `get_cpu_timer()`, CPU MHz helpers, VDSO/task layout constants, `__stackleak_poison()`, `struct thread_struct`, `INIT_THREAD`, `start_thread()`/`start_thread31()`, register display hooks, guarded-storage hooks, task register macros, stack pointer helpers, `stap()`, `__ecag()`, `psw_set_key()`, PSW load/extract helpers, machine-check save/restore, PSW rewind/forward, `disabled_wait()`, `regs_irqs_disabled()`, and `bpon()`.

Control flow: Scheduler and entry code use lowcore to find per-CPU data, set task PSWs and stacks at exec, account CPU timers, manage guarded storage/runtime instrumentation/FPU state in `thread_struct`, and manipulate PSW masks for wait, machine checks, and branch prediction controls.

State and persistence: Persistent state includes per-CPU `pcpu` objects, thread_struct fields in each task, lowcore stack/current pointers, PSW state, timers, guarded-storage/runtime-instrumentation control blocks, and FPU save areas.

Dependencies and integration points: It depends on cpumasks, linkage, irqflags, instruction-pointer helpers, bitops, FPU types, CPU/page/ptrace/setup/runtime-instr/fault definitions, lowcore, and alternatives.

Risks and test signals: PSW and thread layout mistakes break exec, context switch, signals, or machine-check handling. Tests should include 31/64-bit exec, VDSO placement, stackleak, CPU flag hotplug paths, guarded storage, runtime instrumentation, disabled wait/restart, and register dump paths.
