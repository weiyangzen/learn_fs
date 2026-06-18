# sources/distributed-fs/ceph-client/kernel/debug/debug_core.c

## Purpose
`debug_core.c` is the architecture-independent KGDB/KDB core. It manages debugger entry from exceptions, CPU rendezvous, software breakpoints, master/slave CPU state, debugger I/O module registration, sysrq/panic/reboot hooks, optional KGDB console output, early `kgdbwait`, and switching between KDB and GDB remote modes.

## Important APIs, types, and functions
Global state includes `kgdb_info[NR_CPUS]`, `kgdb_connected`, `kgdb_io_module_registered`, `dbg_io_ops`, `kgdb_active`, `masters_in_kgdb`, `slaves_in_kgdb`, `kgdb_break[]`, `kgdb_usethread`, `kgdb_contthread`, `kgdb_single_step`, `kgdb_cpu_doing_single_step`, `dbg_switch_cpu`, `dbg_kdb_mode`, and boot/module parameters `kgdb_use_con` and `kgdbreboot`.

Public functions include weak arch hooks `kgdb_arch_set_breakpoint()`, `kgdb_arch_remove_breakpoint()`, `kgdb_validate_break_address()`, `kgdb_arch_pc()`, `kgdb_arch_init()`, `kgdb_skipexception()`, `kgdb_call_nmi_hook()`, and `kgdb_roundup_cpus()`; breakpoint APIs `dbg_activate_sw_breakpoints()`, `dbg_set_sw_break()`, `dbg_deactivate_sw_breakpoints()`, `dbg_remove_sw_break()`, `kgdb_isremovedbreak()`, `kgdb_has_hit_break()`, `dbg_remove_all_break()`, and `kgdb_free_init_mem()`; entry APIs `kgdb_handle_exception()`, `kgdb_nmicallback()`, `kgdb_nmicallin()`, `kgdb_panic()`, `dbg_late_init()`, `kgdb_register_io_module()`, `kgdb_unregister_io_module()`, `dbg_io_get_char()`, and `kgdb_breakpoint()`.

## Control flow
Software breakpoint setup validates an address by temporarily writing and removing a breakpoint instruction, then records it in `kgdb_break[]` as `BP_SET`. Activation writes all set breakpoints into kernel text and flushes icache where safe; deactivation restores saved instructions; removal marks matching inactive breakpoints removed; remove-all clears both software and architecture hardware breakpoints.

`kgdb_handle_exception()` constructs a `kgdb_state`, rejects non-trap exceptions when `panic_timeout` would auto-reboot, checks recursive entry, and calls `kgdb_cpu_enter()` as a would-be master. `kgdb_cpu_enter()` disables hardware breakpoints, records per-CPU debugger info, arbitrates the master CPU with `dbg_master_lock`, optionally rounds up other CPUs into slave loops, disables active software breakpoints, turns tracing off, and dispatches to `kdb_stub()` or `gdb_serial_stub()`. It handles mode switching, CPU master switching, lockdown blocking of GDB write access, breakpoint reactivation, post-exception hooks, release of slave CPUs, watchdog touches, and IRQ/RCU restoration.

I/O module registration initializes the driver, replaces a deinit-capable existing driver if necessary, registers debugger callbacks, sysrq key, module/reboot notifiers, console output if requested, and triggers `kgdbwait` early breakpoints when possible. Unregistration requires no active GDB connection, unregisters callbacks, clears `dbg_io_ops`, and deinitializes the driver.

## State and persistence behavior
State is entirely in-kernel and volatile. Breakpoints mutate kernel text while active and keep saved instructions in `kgdb_break[]`. Debugger sessions update per-CPU `kgdb_info`, active CPU atomics, master/slave counters, connection mode, and selected thread pointers. Boot parameters persist for the running kernel lifetime. KGDB console registration affects console output routing while enabled.

## Dependencies and integration points
The core integrates with architecture KGDB operations, GDB stub, KDB frontend, sysrq, panic notifier path, reboot notifier, module notifier, console subsystem, security lockdown, SMP call-single/NMI roundup, tracing, watchdogs, RCU stall reset, hardirq state, icache flushing, and blocklisted breakpoint addresses.

## Risks and edge cases
Debugger entry runs in exceptional contexts with interrupts disabled and may stop all CPUs. Recursive entry is dangerous: the code may remove all breakpoints and panic if recursion exceeds one level. Breakpoint writes use nofault kernel memory access and can fail or corrupt text if remove fails. CPU roundup can time out, leaving non-stopped CPUs interfering with debugging. Lockdown can force KDB mode or bail out of GDB. Unregistering an I/O module while connected is a BUG. Early debugging supports pre-percpu environments by using NR_CPUS arrays rather than percpu data.

## Test signals
Signals include software breakpoint set/hit/remove, breakpoints in init memory and `kgdb_free_init_mem()`, hardware breakpoint arch hooks, sysrq-g entry, panic entry with and without `panic_timeout`, `kgdbwait`, replacing I/O modules, `kgdbcon`, reboot notifier detach, KDB/GDB mode switching, CPU switching, single-step on SMP, roundup timeout behavior, lockdown mode, and recursive breakpoint-in-debugger recovery.
