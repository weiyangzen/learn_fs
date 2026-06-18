# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_io.c

## Purpose
This file implements KDB console input and output independent of the architecture. It polls debugger consoles, handles line editing, command history control characters, symbol completion, KGDB remote protocol transition detection, pager prompts, `| grep` output filtering, optional printk logging, and multi-console writes while CPUs are stopped.

## Important APIs, Types, And Functions
`kdb_getchar()` polls `kdb_poll_funcs` and decodes VT100 escape sequences into KDB control codes. `kdb_getstr()` prints the prompt and delegates to `kdb_read()`. `kdb_read()` owns line editing, tab completion through `kallsyms_symbol_complete()` and `kallsyms_symbol_next()`, and special `$?#3f`/`$qSupported` KGDB handoff. `vkdb_printf()` and `kdb_printf()` format output, apply grep and pager behavior, write through `dbg_io_ops`, and optionally mirror output to printk. `kdb_msg_write()` writes to the active KGDB console and other usable consoles.

## Control Flow
Input loops over all registered poll functions, touching the NMI watchdog on each full pass. Escape bytes are accumulated with a two-second polling delay to distinguish bare ESC from arrow/home/end/delete sequences. `kdb_read()` edits the in-memory command buffer, redraws the prompt as needed, completes symbols on the first tab, lists matching symbols on the second tab, and returns complete lines or history control markers. Output is buffered through a 256-byte static buffer; when grep mode is active, complete newline-terminated lines are searched before emission. Pager state increments `kdb_nextline` and prompts once the configured line count is reached.

## State, Persistence, And Dependencies
State includes `kdb_prompt_str`, `kdb_trap_printk`, `kdb_printf_cpu`, `kdb_buffer`, grep accumulation pointers, `suspend_grep`, `kdb_nextline`, `KDB_STATE(PAGER)`, `KDB_STATE(KGDB_TRANS)`, and `KDB_FLAG(CMD_INTERRUPT)`. There is no durable persistence. Dependencies include KGDB I/O ops, console SRCU/NBCON APIs, `printk`, kallsyms, SMP CPU identity, NMI watchdog, and KDB environment variables such as `LINES`, `COLUMNS`, `LOGGING`, `MOREPROMPT`, `SEARCHPROMPT`, and `DTABCOUNT`.

## Integration Points
`kdb_main.c` calls `kdb_getstr()` for commands and most KDB code uses exported `kdb_printf()`. The KGDB transition path calls `kdb_gdb_state_pass()` in `kdb_debugger.c`. Symbol completion depends on `kdb_support.c` wrappers over kallsyms.

## Risks
The output lock is a CPU-owner compare-exchange, so recursive output from the same CPU is tolerated but other CPUs spin with interrupts disabled. Console writes are deliberately reentrant under debugger conditions and rely on selected console drivers tolerating that. Grep buffers can hold partial lines until a newline or prompt. The input path is polling-only with interrupts off, so long escape delays and pager waits are expected but can surprise automation.

## Test Signals
Exercise CR/LF normalization, arrow keys, home/end/delete, tab completion, double-tab listing, KGDB remote `$` packets, `cmd | grep pattern`, `/` search at the pager prompt, `q` pager interruption, `LOGGING=1`, and output on NBCON and classic consoles.
