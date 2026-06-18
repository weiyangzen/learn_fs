## sources/distributed-fs/ceph-client/arch/s390/mm/pfault.c

Purpose: implements z/VM pseudo page fault support, allowing a guest task to sleep when the hypervisor pages in its memory while the virtual CPU runs other work.

Important APIs, types, and functions: boot parameter `nopfault` disables support. `struct pfault_refbk` describes diagnose x'258' init/fini blocks. `__pfault_init()` and `__pfault_fini()` issue the diagnose. `pfault_interrupt()` handles external interrupts. `pfault_cpu_dead()` wakes pending waiters during CPU teardown. `pfault_irq_init()` registers the external IRQ and hotplug callback.

Control flow: early init registers `EXT_IRQ_CP_SERVICE`, initializes the hypervisor feature, registers service-signal subclass, and installs CPU-dead cleanup. Interrupt handling filters subcode, extracts task pid token, references the task, and serializes on `pfault_lock`. Completion interrupts either wake a sleeping task or mark `pfault_wait = -1` if completion won the race. Initial interrupts for current user task set `pfault_wait = 1`, add the thread to `pfault_list`, set state uninterruptible, and request reschedule. CPU dead wakes and dereferences all pending waiters.

State and persistence: persistent globals are `pfault_disable`, `pfault_lock`, and `pfault_list`; per-task state lives in `thread.pfault_wait` and `thread.list`. Hypervisor registration persists until fini.

Dependencies and integration points: depends on s390 external interrupt infrastructure, diagnose x'258', task lookup by pid namespace, scheduler task states, cpuhotplug, and lowcore LPP token layout.

Risks: initial/completion interrupt ordering is explicitly racy and encoded through `pfault_wait` values 1 and -1. The initial interrupt must correspond to `current`; otherwise a warning path avoids sleeping the wrong task. Reference counting must pair list references and interrupt references exactly.

Test signals: z/VM guest paging pressure should show tasks blocking/waking without vCPU stalls. Tests should cover `nopfault`, completion-before-initial, initial-before-completion, CPU offline while tasks wait, module/boot init failure fallback, and absence of stuck `TASK_UNINTERRUPTIBLE` tasks.
