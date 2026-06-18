# sources/distributed-fs/ceph-client/net/ceph/crush/crush_ln_table.h

## Purpose
Provides fixed-point lookup tables used by CRUSH straw2 selection to approximate logarithms without floating-point arithmetic.

## Important APIs, Types, and Functions
The header defines static arrays `__RH_LH_tbl` and `__LL_tbl`. `__RH_LH_tbl` stores reciprocal/log high-part pairs; `__LL_tbl` stores low-part `log2(1 + k/2^15)` values. There are no functions.

## Control Flow
`mapper.c` includes this header and `crush_ln()` indexes the tables to compute a fixed-point logarithm for straw2 draw values.

## State and Persistence
The tables are static read-only data after compilation. They contain no mutable runtime state.

## Dependencies and Integration Points
Depends on kernel or userspace CRUSH integer type definitions. Its values are part of the deterministic CRUSH placement algorithm and must match userspace Ceph.

## Risks
Any table value change alters straw2 placement results. Because the arrays are `static` in a header, each translation unit including it would get a copy; currently it is included by `mapper.c`. The LGPL comment differs from surrounding GPL-only source and should remain consistent with upstream provenance.

## Test Signals
Known-answer tests for `crush_ln()` and straw2 placement, cross-check kernel versus userspace CRUSH mappings, and table-index boundary tests for hash values near 0 and 0xffff.
