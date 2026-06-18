# sources/distributed-fs/ceph-client/arch/hexagon/lib/memcpy.S

## Purpose

`memcpy.S` implements the optimized Hexagon `memcpy` routine with alignment prologue, wide transfer kernel, and epilogue handling. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The public ABI is `memcpy`, using register aliases for source, destination, length, predicates, and wide data buffers. Concrete declarations observed in the file: Macros: `ptr_out`, `ptr_in`, `len`, `data70`, `dataF8`, `ldata0`, `ldata1`, `data1`, `data0`, `ifbyte`, `ifhword`, `ifword`, `noprolog`, `nokernel`, `noepilog`, `align`, `kernel1`, `dalign`, `star3`, `rest`, `back`, `epilog`, `inc`, `kernel`, and 13 more. Assembly entry labels: `memcpy`, `.Lskip64`, `.Lnoprolog32`, `.Ldword_loop_prolog`, `.Lkernel`, `.Loword_loop_25to31`, `.Lodd_alignment`, `.Loword_loop_00to24`, `.Lepilog`, `.Ldword_loop_epilog`, `.Lepilog60`, `.Lbytes23orless`, `.Lbyte_copy`, `.Ldwordaligned`, `.Ldword_copy`, `.Lmemcpy_return`.

## Control Flow, State, And Persistence

Runtime flow aligns the destination/source relationship, handles small/prologue bytes, copies large blocks in 32-byte chunks, and finishes with word/half/byte epilogues.

## Dependencies And Integration Points

It integrates with core kernel memory operations and module exports through `hexagon_ksyms.c`.

## Risks And Test Signals

Risks are overlap assumptions, unaligned faults, tail corruption, and clobber/calling-convention bugs. Test signals are lib/string tests, KASAN-free boot, module use of memcpy, and randomized copy verification.
 A local static signal for this file is that it has 530 lines and 15374 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
