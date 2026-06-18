# sources/distributed-fs/ceph-client/arch/um/os-Linux/smp.c

## Purpose
Provides host pthread and realtime-signal mechanics for UML SMP virtual CPUs and IPIs.

## Important APIs, Types, and Functions
`uml_curr_cpu()` returns thread-local CPU id. `os_start_cpu_thread()` creates a masked pthread for a CPU. `os_start_secondary()` restores masks and longjmps into the UML idle-thread context. `os_send_ipi()` sends `IPI_SIGNAL` with vector data. `os_local_ipi_enable()`/`os_local_ipi_disable()` manage local IPI masking. `os_init_smp()` installs the realtime signal handler and records boot CPU pthread.

## Control Flow, State, and Persistence
Persistent state includes thread-local `__curr_cpu` and `cpu_threads[]`. Each AP starts with all signals blocked, receives boot data, then transitions into kernel-side `uml_start_secondary()` and later unblocks relevant signals.

## Dependencies and Integration Points
Pairs with `kernel/smp.c`, host signal state in `signal.c`, and pthread APIs. IPI values are delivered as `sigqueue` payloads and handled on the alternate signal stack.

## Risks and Test Signals
Risks include signal-mask mistakes, lost vector payloads, CPU thread creation failures, and pthread lifetime assumptions. Test multi-CPU boot, IPI storms, call_function, rescheduling, local IRQ disable/enable, and shutdown.
