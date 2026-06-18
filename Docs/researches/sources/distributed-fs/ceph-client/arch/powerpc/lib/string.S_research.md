<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S

## Purpose
This assembly file provides generic PowerPC implementations of `strncpy`, `strncmp`, and `memchr` for the kernel.

## Important APIs, types, and functions
It exports `_GLOBAL(strncpy)`, `_GLOBAL(strncmp)`, and `_GLOBAL(memchr)` with `EXPORT_SYMBOL`. The code uses `PPC_LCMPI`, counted loops through CTR, byte load/store update instructions, and `IFETCH_ALIGN_BYTES` alignment.

## Control flow
`strncpy` copies bytes until `n` is exhausted or a NUL is found, then zero-fills the remaining destination bytes. `strncmp` walks both strings until count expires, a NUL is seen, or bytes differ, returning the subtraction result. `memchr` scans a byte range and returns the matching address or zero.

## State and persistence behavior
The functions mutate only caller-provided destination memory for `strncpy`; all state is transient in registers and CTR. There are no exception table entries, so callers must provide valid kernel addresses.

## Dependencies and integration points
These are architecture string primitives linked into the PowerPC kernel and exported for other built-in or modular users.

## Risks and edge cases
Correctness depends on PPC condition-register and CTR branch forms. Boundary cases are zero length, exact NUL at the last byte, zero-fill behavior for `strncpy`, and unsigned byte comparison behavior in `strncmp`.

## Test signals
Signals are ordinary kernel string tests or boot/module users exercising exported symbols; no local self-test exists in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/string.S -->
