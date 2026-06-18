# sources/distributed-fs/ceph-client/scripts/gdb/vmlinux-gdb.py

## Purpose
`vmlinux-gdb.py` is the entry loader for the Linux kernel GDB helper suite. It updates `sys.path`, verifies GDB capability, rejects reduced debug info, and imports helper modules for command registration.

## Important APIs, Types, and Functions
The file has no exported functions. Its behavior is import side effects: importing `linux.constants`, `utils`, `symbols`, `modules`, `dmesg`, `tasks`, `config`, `cpus`, `lists`, `rbtree`, `proc`, `timerlist`, `clk`, `genpd`, `device`, `vfs`, `pgtable`, `radixtree`, `interrupts`, `mm`, `stackdepot`, `page_owner`, `slab`, `vmalloc`, and `kasan`.

## Control Flow
It inserts the scripts directory, probes minimal GDB Python expression/execution support, then imports modules. If `CONFIG_DEBUG_INFO_REDUCED` is true, it raises because type-complete scripts would be unreliable.

## State and Persistence Behavior
It mutates the Python import path and registers many GDB commands/functions through imported module side effects.

## Dependencies and Integration Points
This is sourced by GDB when debugging vmlinux and is the integration point for all listed GDB helpers.

## Risks and Test Signals
The script references `sys` and `gdb` without importing them locally, relying on GDB's execution environment. Path construction assumes the kernel scripts layout. Test by sourcing it in GDB with full and reduced debug-info kernels and checking command registration.
