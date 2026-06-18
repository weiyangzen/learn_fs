# sources/distributed-fs/ceph-client/arch/riscv/kernel/cpu_ops_spinwait.c

Purpose: Implements legacy spinwait secondary CPU boot for systems without SBI HSM.

Important APIs/types/functions: Defines `cpu_ops_spinwait`, `__cpu_spinwait_stack_pointer[]`, `__cpu_spinwait_task_pointer[]`, and `spinwait_cpu_start()`.

Control flow: Boot CPU writes the idle task and stack pointer into per-CPU arrays, then the secondary hart spinning in `head.S` observes nonzero values, fences, and enters the common secondary start path.

State and persistence: Persistent boot arrays in `.data` coordinate one-time secondary bringup and later hotplug-like starts where supported.

Dependencies and integration points: Tied to `CONFIG_RISCV_BOOT_SPINWAIT`, `head.S` spinwait loops, SMP setup, and CPU hotplug expectations.

Risks and test signals: Missing ordering or stale pointers can boot a hart on the wrong stack or task. Test legacy DT boot paths, high hart IDs, multiple secondary starts, and memory-ordering stress under emulators.
