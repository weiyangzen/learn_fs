# sources/distributed-fs/ceph-client/arch/sh/lib/strlen.S

Purpose: implements the standard `strlen` primitive for SH.

Important symbol: `ENTRY(strlen)`.

Control flow: scans byte-by-byte or word-assisted until a NUL terminator is found, then returns the number of bytes before it.

State and persistence: read-only over the string; no persistent state.

Dependencies and integration: core kernel string function.

Risks: must never read invalid memory beyond acceptable primitive behavior; return count must exclude the terminator.

Test signals: string selftests for empty, one-byte, long, and unaligned strings.
