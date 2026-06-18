# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_bp.c

## Purpose
`kdb_bp.c` implements KDB breakpoint and single-step commands. It maintains the KDB breakpoint table, parses `bp`/`bph` commands, installs/removes breakpoints through KGDB core and architecture hardware-breakpoint hooks, and registers `bp`, `bl`, `bc`, `be`, `bd`, `ss`, and optional `bph` commands.

## Important APIs, types, and functions
Global state is `kdb_breakpoints[KDB_MAXBPT]`, an array of `kdb_bp_t`. Important helpers include `kdb_setsinglestep()`, `kdb_bptype()`, `kdb_parsebp()`, `_kdb_bp_remove()`, `kdb_handle_bp()`, `_kdb_bp_install()`, `kdb_bp_install()`, `kdb_bp_remove()`, `kdb_printbp()`, command handler `kdb_bp()`, command handler `kdb_bc()`, command handler `kdb_ss()`, and initializer `kdb_initbptab()`.

## Control flow
`kdb_initbptab()` clears the breakpoint table, marks all entries free, registers core breakpoint commands, and registers `bph` only if architecture KGDB ops advertise hardware breakpoint support. `kdb_bp()` with no arguments lists active entries. With an address, it parses the symbol/address, validates software breakpoint ability immediately, allocates a free table slot, parses hardware type and length for `bph`, rejects duplicate addresses, enables the entry, and prints it.

`kdb_bp_install()` runs before leaving KDB and installs enabled breakpoints. Software breakpoints call `dbg_set_sw_break()`, while hardware breakpoints call `arch_kgdb_ops.set_hw_breakpoint()`. Delayed breakpoints and single-step state are handled by setting KDB single-step flags and marking the breakpoint delayed. `kdb_bp_remove()` runs on debugger entry in reverse order and removes installed breakpoints through KGDB or arch hooks.

`kdb_bc()` implements clear, enable, and disable for a breakpoint number, address, or `*`. Clearing marks entries free; disabling leaves them allocated but inactive. `kdb_ss()` sets KDB single-step state and returns `KDB_CMD_SS`.

## State and persistence behavior
State persists only during the running kernel debugger session in `kdb_breakpoints` and KDB state flags such as `DOING_SS` and `SSBPT`. Active software breakpoints are also reflected in the KGDB core breakpoint table and temporarily modify kernel text when activated. No filesystem state is written.

## Dependencies and integration points
The file depends on KDB command registration/parsing helpers, KGDB software breakpoint APIs, `arch_kgdb_ops` hardware breakpoint support, KDB state macros, symbol printing, SMP/scheduling context, and architecture instruction-pointer access.

## Risks and edge cases
Breakpoint installation can fail when kernel text is read-only or blocked, and the user-facing message suggests `rodata=off` or hardware breakpoints. Duplicate detection is address-only, so it disallows separate read/write hardware breakpoints on the same address. Delayed breakpoint handling around single-step is subtle and depends on KDB state flags. Hardware length is limited to 8 bytes. Breakpoints in KDB internals are intentionally delayed until leaving the debugger, but mistakes can trigger recursive debugger entry.

## Test signals
Exercise listing with no breakpoints, setting software `bp`, setting hardware `bph inst`, `datar`, and `dataw` with lengths, duplicate-address rejection, table-full behavior, invalid addresses, `bc`, `bd`, `be` by number/address/star, delayed breakpoints with single-step, install/remove ordering, unsupported hardware breakpoint builds, and rodata-protected software breakpoint failure.
