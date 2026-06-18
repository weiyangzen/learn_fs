# sources/distributed-fs/ceph-client/include/linux/kgdb.h

## Purpose

`kgdb.h` defines the shared API between KGDB core code, architecture code, and KGDB I/O drivers. It covers breakpoint representation, register conversion, exception handling, CPU roundup, remote GDB packet helpers, and stubs for non-KGDB builds. The source was read as a complete 356-line file.

## Important APIs, Types, and Functions

Important state and types include `kgdb_connected`, `kgdb_active`, `kgdb_setting_breakpoint`, `kgdb_cpu_doing_single_step`, `enum kgdb_bptype`, `enum kgdb_bpstate`, `struct kgdb_bkpt`, `struct dbg_reg_def_t`, `struct kgdb_arch`, and `struct kgdb_io`. APIs include `kgdb_breakpoint()`, `kgdb_arch_init()`, `kgdb_arch_exit()`, `pt_regs_to_gdb_regs()`, `sleeping_thread_to_gdb_regs()`, `gdb_regs_to_pt_regs()`, `kgdb_arch_handle_exception()`, `kgdb_roundup_cpus()`, `kgdb_arch_set_pc()`, `kgdb_register_io_module()`, `kgdb_handle_exception()`, `kgdb_nmicallback()`, and `kgdb_panic()`.

## Control Flow

An exception or explicit breakpoint enters KGDB, architecture code converts registers and handles arch-specific commands, the I/O module exchanges packets with GDB, and KGDB may single-step, continue, set breakpoints, or round up other CPUs. `kgdb_within_blocklist()` optionally shares the kprobe blacklist to avoid probing/debugging unsafe addresses.

## State and Persistence Behavior

Breakpoint slots preserve original instructions and state while active. KGDB connection, selected threads, active CPU, and registered I/O module are global kernel state. There is no durable persistence.

## Dependencies and Integration Points

It integrates with `asm/kgdb.h`, `pt_regs`, kprobes blacklist logic, consoles or serial drivers implementing `struct kgdb_io`, NMI callbacks, SMP CPU coordination, and architecture breakpoint/register code.

## Risks and Edge Cases

KGDB runs in exception/NMI-like contexts, so callbacks must be reentrant and avoid unsafe locks. Breakpoint instruction sizes and register layouts are architecture-specific. Missing blocklist support may permit breakpoints in unsafe code. Non-KGDB builds stub many APIs, hiding runtime behavior from generic compilation.

## Test Signals

Architecture KGDB selftests, remote GDB attach/continue/single-step tests, hardware breakpoint tests, SMP roundup tests, panic entry tests, I/O module register/unregister tests, and `CONFIG_KGDB=n` build coverage are useful.
