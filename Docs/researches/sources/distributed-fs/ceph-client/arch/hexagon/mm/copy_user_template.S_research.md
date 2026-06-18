# sources/distributed-fs/ceph-client/arch/hexagon/mm/copy_user_template.S

## Purpose

`copy_user_template.S` is the shared assembly body for Hexagon raw user-copy routines. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The including file defines register aliases and `FUNCNAME`; template labels implement aligned and unaligned 8/4/2/1-byte loops with extable-visible fault sites. Concrete declarations observed in the file: Assembly entry labels: `FUNCNAME`, `.Loop8`, `.Loop_not_aligned_8`, `.Loop4`, `.Loop_not_aligned_4`, `.Loop2`, `.Loop_not_aligned`, `.Loop1`, `.Lsmall`, `.Ldone`, `.Lalign`.

## Control Flow, State, And Persistence

Runtime flow prefers 8-byte transfers, falls back through smaller chunks for alignment/tail, and returns the uncopied byte count after fixup.

## Dependencies And Integration Points

It integrates with `copy_from_user.S`, `copy_to_user.S`, `uaccess.c`, and architecture exception-table handling.

## Risks And Test Signals

Risks are template changes breaking both copy directions or exception label numbering. Test signals are fault-injection uaccess tests and randomized partial-copy tests.
 A local static signal for this file is that it has 173 lines and 2667 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
