# sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.c

## Purpose
`nonstdio.c` implements xmon's minimal console I/O layer on top of `udbg`, including character input, line editing, printf-style output, and optional pagination for long debugger output.

## Important APIs, Types, And Functions
Public functions are `xmon_start_pagination`, `xmon_end_pagination`, `xmon_set_pagination_lpp`, `xmon_putchar`, `xmon_gets`, `xmon_printf`, and `xmon_puts`. Internal helpers include `xmon_readchar`, `xmon_write`, and `xmon_getchar`. Static state includes pagination flags, lines-per-page, current line count, a 256-byte input line buffer, and a 1024-byte printf output buffer.

## Control Flow
Output flows through `xmon_write`, which optionally paginates on newline boundaries, prompts after the configured number of lines, and accepts `a` for all output, `q` for truncation, or any other key for the next page. `xmon_putchar` translates newline to CRLF. Input is line buffered: it reads from `udbg_getc`, echoes characters, handles backspace/delete and Ctrl-U, rings the bell on overflow, and returns buffered characters to `xmon_gets`.

## State And Persistence
All state is in static memory and lasts for the running kernel. Pagination state persists across xmon output until explicitly ended. Input and output buffers are shared, not per-caller, matching xmon's single-console use.

## Dependencies And Integration Points
It depends on `udbg_getc`, `udbg_write`, kernel `vsnprintf`, `pr_cont` fallback output, and declarations from `nonstdio.h`. Higher-level xmon commands and the disassembler use this instead of libc stdio.

## Risks
The static buffers are not reentrant. If no `udbg` hooks are installed, `xmon_printf` can fall back to `printk` continuation output, which the source labels dangerous. Pagination can drop output after `q` while still reporting bytes consumed to callers. Input editing is limited to simple control characters and fixed line size.

## Test Signals
Manual xmon sessions validate line editing, CRLF output, pagination prompts, truncation, and fallback output. Build coverage ensures `__printf` users match format arguments through the header declaration.
