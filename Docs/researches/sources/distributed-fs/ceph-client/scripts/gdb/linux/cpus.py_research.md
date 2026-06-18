# sources/distributed-fs/ceph-client/scripts/gdb/linux/cpus.py

Purpose: Provides GDB helpers for per-CPU variables, CPU masks, and current task lookup.

Important APIs/classes: `get_current_cpu()`, `per_cpu()`, `cpu_list()`, `each_online_cpu()`, `each_present_cpu()`, `each_possible_cpu()`, `each_active_cpu()`, `LxCpus`, GDB functions `$lx_per_cpu`, `$lx_per_cpu_ptr`, `get_current_task()`, and `$lx_current`.

Control flow: Current CPU is derived from QEMU thread number or KGDB active counter. `per_cpu()` adds the architecture per-CPU offset to a variable pointer, with sparc and !SMP cases handled. CPU mask iteration caches `.bits` arrays until stop/new_objfile events invalidate the cache. Current task lookup handles x86/UML, aarch64 using `SP_EL0`, and riscv `tp`/`sscratch`.

State/persistence: `cpu_mask` cache stores GDB values and connects invalidation handlers after first use. Commands/functions are registered at import.

Dependencies/integration: GDB Python API, `linux.tasks`, `linux.utils`, kernel per-CPU symbols, CPU masks, and architecture registers.

Risks: Current CPU/task support is limited by gdbserver type and architecture. CPU mask cache must be invalidated on target changes. `MAX_CPUS` is defined but not enforced in `cpu_list()`. aarch64 rejects user-mode context.

Test signals: QEMU and KGDB sessions, SMP and !SMP, x86/UML/aarch64/riscv current task, CPU hotplug mask changes, and per-CPU variable dereference.
