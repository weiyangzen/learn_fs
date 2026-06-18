# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/ex.S

## Purpose
`ex.S` builds the SH3 exception dispatch table consumed by `entry.S`.

## Important APIs, Types, And Functions
It defines fallback aliases from many exception labels to `exception_error` when optional features are not present, aliases KGDB and FPU handlers conditionally, and exports `exception_handling_table`.

## Control Flow
`entry.S` converts the exception event code into an offset and indexes `exception_handling_table`. The table entries point to concrete handlers such as TLB miss handlers, address-error handlers, TRAPA/syscall logic from common entry code, optional FPU/KGDB handlers, or `exception_none`/`exception_error`.

## State And Persistence
There is no mutable state. The table is static dispatch data linked into the low-level exception path.

## Dependencies And Integration Points
It depends on symbols provided by `entry.S`, common SH exception code, KGDB, and FPU trap code depending on configuration. SH4 also reuses this table through its Makefile.

## Risks
Table order must match hardware exception vector encoding and `entry.S` indexing. Wrong fallback aliases can turn recoverable faults into fatal `exception_error` paths or mask unsupported features incorrectly.

## Test Signals
Exception-path smoke tests, syscall/TRAPA tests, KGDB trap tests when configured, and page-fault tests validate that the dispatch table points to the expected handlers.
