# sources/distributed-fs/ceph-client/arch/powerpc/xmon/nonstdio.h

## Purpose
`nonstdio.h` exposes xmon's minimal stdio replacement and maps familiar names to xmon-specific console routines.

## Important APIs, Types, And Functions
It defines `EOF` as `-1`, declares pagination controls, `xmon_putchar`, `xmon_puts`, `xmon_gets`, and `xmon_printf`, and maps `printf` to `xmon_printf` and `putchar` to `xmon_putchar`.

## Control Flow
The header has no runtime flow, but the macros redirect imported or debugger code that calls `printf`/`putchar` into xmon's `udbg`-backed I/O path.

## State And Persistence
No state is defined here; implementation state lives in `nonstdio.c`.

## Dependencies And Integration Points
It depends on kernel `__printf` annotation support and is included by xmon code and the binutils-derived disassembler.

## Risks
The `printf` and `putchar` macros are broad and can surprise code included after this header. The header intentionally provides only a tiny subset of stdio, so imported code must not require full libc behavior.

## Test Signals
Successful xmon and disassembler builds validate macro compatibility. Runtime xmon command output validates redirection through `xmon_printf`.
