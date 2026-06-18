# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_main.c

## Purpose
This is KDB's architecture-independent command engine. It owns command registration, command parsing, environment variables, command history, macro definitions, lockdown-aware command permissions, the per-CPU main debugger loop, and the built-in commands for memory, registers, process state, CPU switching, dmesg, sysrq, reboot, signals, system summary, and per-CPU data.

## Important APIs, Types, And Functions
Global state includes `kdb_flags`, `kdb_state`, `kdb_initial_cpu`, `kdb_current_task`, `kdb_current_regs`, grep globals, command history buffers, and the `kdb_cmds_head` list. Important helpers are `kdbgetenv()`, `kdbgetintenv()`, `kdb_set()`, `kdbgetaddrarg()`, `kdb_parse()`, `kdb_local()`, `kdb_main_loop()`, `kdb_register()`, `kdb_register_table()`, `kdb_unregister()`, and `kdb_init()`. Built-in command handlers include `kdb_md()`, `kdb_mm()`, `kdb_go()`, `kdb_rd()`, `kdb_rm()`, `kdb_dmesg()`, `kdb_cpu()`, `kdb_ps()`, `kdb_pid()`, `kdb_kgdb()`, `kdb_help()`, `kdb_kill()`, `kdb_summary()`, and `kdb_per_cpu()`.

## Control Flow
`kdb_main_loop()` waits while this CPU is held as a slave, exits if another CPU is leaving, otherwise calls `kdb_local()`. `kdb_local()` prints the entry reason, checks lockdown, then repeatedly prompts through `kdb_getstr()`, handles command history controls, parses commands, reports diagnostics, and breaks on `go`, CPU switch, single-step, or KGDB transition. `kdb_parse()` tokenizes in place, handles comments, `| grep`, macros, command abbreviation, permission checks, command repeat semantics, and address-expression fallback. Initialization registers the built-in table, initializes breakpoints, and replays boot-time `kdb_cmds`.

## State, Persistence, And Dependencies
KDB environment values live in the fixed `__env[31]` table and may allocate replacement strings. Macros allocate `struct kdb_macro` and statement strings. Memory display remembers last address/radix/width/repeat. Command history is a 32-entry static ring. Security state is derived from `kdb_cmd_enabled` and kernel lockdown checks. Dependencies include kallsyms, KGDB per-CPU state, ptrace register definitions, scheduler/task iteration, printk/kmsg dump, sysrq, reboot, signals, sysinfo, CPU masks, and KDB support routines for safe memory/symbol access.

## Integration Points
`kdb_debugger.c` enters `kdb_main_loop()`. `kdb_io.c` supplies command I/O and grep output behavior. `kdb_support.c` supplies symbol lookup, memory reads/writes, and task-state formatting. Other KDB files register commands through the exported registration functions.

## Risks
The parser uses static `argv` and `cbuf`, so recursive parse paths must avoid using old argument pointers. Command permission masks are security-sensitive, especially memory/register read/write and flow control under lockdown. Memory write/register write commands can alter a live kernel. Macro definition allocates memory in debugger context and must force-close incomplete `defcmd` blocks. CPU switching and catastrophic continue behavior depend on precise KDB state flags.

## Test Signals
Cover command abbreviation and repeat, `set`/`env`, `KDBDEBUG`, `defcmd`/`endefcmd`, address parsing with symbols/env/offsets, `md` variants including physical and symbolic reads, `mm`, `go` on initial versus non-initial CPU, `cpu`, `pid`, `ps` filters, `dmesg` ranges, sysrq, `kill`, lockdown permission denial, and transition to KGDB.
