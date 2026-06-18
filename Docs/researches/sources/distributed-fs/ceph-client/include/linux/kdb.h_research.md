# sources/distributed-fs/ceph-client/include/linux/kdb.h

## Purpose
Declares the architecture-independent KDB kernel debugger command interface, permissions, flags, return codes, entry reasons, polling hooks, and registration APIs.

## Important APIs, Types, And Functions
`kdb_cmdflags_t` encodes command permission classes, no-argument permissions, and repeat behavior. `kdb_func_t` and `kdbtab_t` describe commands. With `CONFIG_KGDB_KDB`, the header exports KDB state flags, return codes, entry reasons, message sources, `kdb_printf()`, `vkdb_printf()`, `kdb_init()`, poll functions, keyboard polling, `kdb_process_cpu()`, `kdb_send_sig()`, kallsyms walking, and command register/unregister APIs. Stubs are provided when KDB is disabled.

## Control Flow
KDB enters for explicit traps, breakpoints, oops, NMI, keyboard, recursion, and single-step reasons. Commands are looked up in the command table and gated by permission flags. Poll functions provide input while normal scheduling may be stopped.

## State And Persistence
Runtime state includes global flags, initial CPU, poll function table, command list, environment variables, last die message, and printk redirection state. It is in-memory debug state only.

## Dependencies And Integration Points
Depends on KGDB/KDB config, list, SMP, scheduler, atomics, kallsyms, keyboard polling, and printk. Integrates with debugger traps, console/VT input, module listing, signal delivery, and command extensions.

## Risks
KDB commands can read/write memory and registers or reboot the system, so permission flags are significant. Debugger contexts may be atomic or catastrophic, so commands must avoid unsafe blocking. Disabled builds silently stub registration and printing.

## Test Signals
Signals include KGDB/KDB boot and early KDB tests, command permission checks, keyboard polling, command registration/unregistration, kallsyms walking, per-CPU entry behavior, and no-op behavior when disabled.
