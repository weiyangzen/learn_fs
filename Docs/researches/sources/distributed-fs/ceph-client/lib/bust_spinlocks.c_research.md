# sources/distributed-fs/ceph-client/lib/bust_spinlocks.c

## Purpose

`sources/distributed-fs/ceph-client/lib/bust_spinlocks.c` provides the generic `bust_spinlocks()` implementation for architectures without their own version. It helps panic/oops paths get console output out despite normal console locking constraints.

## Important APIs, Types, and Functions

The single function is `bust_spinlocks(int yes)`. It manipulates global `oops_in_progress`, calls `console_unblank()`, and wakes the printk/klogd path with `wake_up_klogd()`.

## Control Flow

When `yes` is nonzero, it increments `oops_in_progress`. When `yes` is zero, it unblanks the console, decrements `oops_in_progress`, and wakes logging if the count reaches zero.

## State and Persistence Behavior

The only persistent state is the global oops nesting count. It is intentionally process-global and affects console/printk behavior during exceptional paths.

## Dependencies and Integration Points

The function integrates with `oops`, `die`, `BUG`, and panic reporting paths, plus console, VT, printk, and waitqueue infrastructure.

## Risks and Edge Cases

The count must remain balanced across nested exceptional paths. Underflow would incorrectly wake logging and mark the system as out of oops context. This function runs when normal locking may already be compromised, so it intentionally stays minimal.

## Test Signals

Signals include arch link coverage, nested `bust_spinlocks(1)`/`bust_spinlocks(0)` balance, console unblank on exit, and printk wakeup only when the nesting counter reaches zero.

## Read Coverage

Source read size: 29 lines, 632 bytes.
