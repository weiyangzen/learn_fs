# sources/distributed-fs/ceph-client/arch/sh/lib/copy_page.S

Purpose: provides optimized page copy and user-copy routines for MMU-enabled SH.

Important symbols: `copy_page`, `__copy_user`, alignment jump tables, cleanup labels, and exception-table recovery paths.

Control flow: `copy_page` copies one page using aligned register bursts. `__copy_user` handles arbitrary source/destination alignment, copies in longword chunks where possible, cleans up trailing bytes, and on fault computes remaining bytes before returning.

State and persistence: mutates destination kernel or user memory; returns residual byte counts for user-copy semantics.

Dependencies and integration: depends on `PAGE_SIZE`, uaccess exception tables, and generic memory-management copy paths.

Risks: alignment dispatch and exception cleanup must agree exactly with copied byte progress. Incorrect residual counts break hardened user-copy callers.

Test signals: page-copy stress tests, user-copy fault injection, copy across page boundaries, and memory corruption checks under MMU.
