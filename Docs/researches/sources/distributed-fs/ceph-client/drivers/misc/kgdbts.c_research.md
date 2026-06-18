# sources/distributed-fs/ceph-client/drivers/misc/kgdbts.c

## Purpose
`kgdbts.c` is the in-kernel KGDB test suite. It registers a fake `kgdb_io` transport that emulates GDB remote protocol packets to validate software breakpoints, hardware breakpoints, single stepping, bad memory reads, optional NMI behavior, and breakpoint stress on `kernel_clone` or `do_sys_openat2`.

## Important APIs, types, and functions
Test scripting uses `struct test_struct` and `struct test_state`. Packet generation/validation uses `fill_get_buf`, `run_simple_test`, and `validate_simple_test`. Breakpoint helpers include `sw_break`, `hw_break`, removal variants, write/access hardware break helpers, `check_and_rewind_pc`, and `check_single_step`. Top-level runners are `kgdbts_run_tests`, `configure_kgdbts`, and `init_kgdbts`. KGDB integration is through `kgdbts_io_ops`, `kgdb_register_io_module`, `kgdb_unregister_io_module`, `kgdb_breakpoint`, and module parameter `kgdbts`.

## Control flow
Configuration arrives from the `kgdbts=` boot option or sysfs module parameter. `configure_kgdbts` optionally runs an early plant/detach sanity test, registers the fake I/O module, and starts `kgdbts_run_tests`. Each test is a table of expected get/put packets. During KGDB exceptions, `read_char` feeds scripted packets to KGDB, while `write_char` accumulates KGDB responses, validates them, advances the table index, and schedules ACKs. Optional long-running clone/open tests spawn a thread that unregisters the I/O module after a final ACK.

## State and persistence
The suite is stateful through file-scope buffers, counters, config string, breakpoint target addresses, thread ids, single-step emulation state, and a configured flag. It has no persistent storage; state lasts until tests complete or the module parameter is changed. It intentionally manipulates kgdb global debugger state and module references during exception entry/exit.

## Dependencies and integration points
The file depends on KGDB internals, kallsyms lookup, architecture register conversion helpers, breakpoint instruction size definitions, NMI watchdog touching, kthreads, and syscall symbol names. Architecture quirks are handled for emulated single-step and adjusted breakpoint offsets.

## Risks
This code intentionally triggers breakpoints and debugger paths, so it can hang or destabilize a system when KGDB or architecture support is broken. Symbol-name drift (`do_sys_openat2`, `kernel_clone`) affects optional tests. The packet tables rely on GDB remote protocol details. The static lookup cache is intentionally non-reentrant because debug traps stop other CPUs.

## Test signals
Expected signals are `kgdbts:RUN` messages, lack of `ERROR PUT` validation failures, successful unregister after final ACK, and no memory change after plant/detach. Coverage should include boot-time `kgdbts=V1 kgdbwait`, runtime sysfs invocation, hardware breakpoint capable and incapable architectures, single-step emulation architectures, and optional `F`, `S`, `I`, and `N` modes.
