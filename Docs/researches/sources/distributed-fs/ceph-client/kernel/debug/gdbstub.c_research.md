# sources/distributed-fs/ceph-client/kernel/debug/gdbstub.c

## Purpose
`gdbstub.c` implements the GDB remote serial protocol for KGDB. It translates packets from a host GDB into kernel register access, memory reads/writes, breakpoint control, thread queries, qRcmd KDB commands, continue/single-step requests, detach/kill, and emergency reboot.

## Important APIs, types, and functions
Static buffers `remcom_in_buffer`, `remcom_out_buffer`, and `gdbmsgbuf` hold protocol packets. `gdb_regs` stores architecture registers in GDB format. Core packet helpers are `gdbstub_read_wait()`, `get_packet()`, `put_packet()`, and `gdbstub_msg_write()`. Conversion helpers include `kgdb_mem2hex()`, `kgdb_hex2mem()`, `kgdb_hex2long()`, `kgdb_ebin2mem()`, `pt_regs_to_gdb_regs()`, and `gdb_regs_to_pt_regs()`.

Command handlers include `gdb_cmd_status()`, `gdb_cmd_getregs()`, `gdb_cmd_setregs()`, `gdb_cmd_memread()`, `gdb_cmd_memwrite()`, register get/set handlers, `gdb_cmd_binwrite()`, `gdb_cmd_detachkill()`, `gdb_cmd_reboot()`, `gdb_cmd_query()`, `gdb_cmd_task()`, `gdb_cmd_thread()`, `gdb_cmd_break()`, and `gdb_cmd_exception_pass()`. Public entry points are `gdb_serial_stub()`, `gdbstub_state()`, and `gdbstub_exit()`.

## Control flow
`gdb_serial_stub()` initializes selected-thread state, optionally sends a `T` stop reply when already connected, then loops reading `$packet#checksum` frames with `get_packet()`. It dispatches by first packet character, fills `remcom_out_buffer`, and sends a reply with `put_packet()` unless a continue/detach/kill path exits to the KGDB core. Unsupported or arch-specific commands fall through to `kgdb_arch_handle_exception()`.

Memory and register commands use nofault kernel copy helpers and arch register accessors. Breakpoint packets call KGDB software breakpoint APIs for type 0 or architecture hardware breakpoint hooks for supported types. Thread packets map idle CPU contexts to negative shadow PIDs and normal tasks to init PID namespace PIDs. Query packets enumerate CPUs and tasks in batches, return current thread, provide thread extra info, pass `qRcmd` payloads into KDB when configured, and delegate architecture qXfer features when available.

`gdbstub_state()` lets KDB transition commands feed commands back into the GDB stub, including saved packet replay. `gdbstub_exit()` sends a minimal `Wxx` exit packet during reboot if connected and in GDB mode.

## State and persistence behavior
State is session-scoped and static in the kernel. `kgdb_connected`, `kgdb_usethread`, `kgdb_contthread`, per-session fields in `kgdb_state`, replay-buffer counters, and selected register images are mutated. Memory write packets can modify arbitrary kernel memory and flush icache where safe. No filesystem persistence exists, but writes and breakpoints can permanently affect the running kernel until reboot or repair.

## Dependencies and integration points
The stub depends on KGDB I/O operations, debug core state, KDB polling and parser hooks when enabled, architecture register definitions and exception handlers, nofault kernel memory access, PID/task iteration, init PID namespace, emergency reboot, cache flushing, and optional architecture qXfer packet support.

## Risks and edge cases
The packet parser is intentionally simple and runs with the system stopped; malformed packets are retried by checksum NAKs. Memory/register write commands are powerful and are blocked only by higher-level KGDB lockdown logic in the core. Buffer sizes limit packet payloads; `kgdb_mem2hex()` uses the upper half of the output buffer as a raw-copy staging area, so callers must keep requested lengths within protocol buffer assumptions. Thread enumeration races are mitigated by KGDB stopping CPUs and using RCU-friendly PID lookup, but sleeping tasks only expose switch-saved register state. Detach/kill remove all breakpoints and return to default arch handling.

## Test signals
Test with host GDB attach/status, register read/write, memory read/write hex and binary forms, software and hardware breakpoint set/remove, continue, single-step, detach, kill, emergency reboot packet `R0`, thread list batching, CPU shadow thread access, thread extra info, qRcmd KDB commands, unsupported packet fallback, checksum retry behavior, console `O` packets, and reboot `Wxx` exit notification.
