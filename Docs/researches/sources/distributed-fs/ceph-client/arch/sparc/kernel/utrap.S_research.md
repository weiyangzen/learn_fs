<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S

## Purpose
Implements SPARC64 user-trap dispatch for trap-table `TRAP_UTRAP` entries, invoking per-thread user trap handlers when registered or falling back to `bad_trap`.

## Important APIs, Types, And Functions
Exports `utrap_trap`. It reads `TI_UTRAPS`, indexes the handler table by the trap number in `%g3`, and calls `bad_trap` through `etrap`/`rtrap` when no table is present.

## Control Flow
On entry, the code loads current thread info and checks for a user-trap table. Without one it builds a normal trap frame and reports a bad trap. With a table, it loads the target handler, creates a new register window, updates `tstate` CWP, preserves original TPC/TNPC in locals, writes the handler into `%tnpc`, and executes `done` so user execution resumes at the handler path.

## State And Persistence
Persistent state is the per-thread `TI_UTRAPS` pointer maintained elsewhere. This routine mutates trap registers, CWP, and the user-visible control-flow target for immediate delivery.

## Dependencies And Integration Points
Used by `ttable_64.S` user-trap vectors and depends on thread-info layout, `etrap`, `rtrap`, `bad_trap`, and SPARC V9 trap-return semantics.

## Risks And Edge Cases
Handler table indexing assumes `%g3` is a valid user-trap index from the macro caller. The `done` path is sensitive to exact TPC/TNPC semantics. Missing table fallback must preserve the trap level for `bad_trap`.

## Test Signals
Signals include registered user trap handlers receiving software trap control, unregistered user traps producing bad-trap SIGILL behavior, and 32/64-bit user trap compatibility cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/utrap.S -->
