# sources/distributed-fs/ceph-client/arch/s390/kernel/diag/diag.c

## Purpose
Provides common s390 diagnose instruction wrappers, per-CPU diagnose usage statistics, tracepoint integration, and AMODE31 operation pointers.

## Important APIs, Types, And Functions
Exports `diag_stat_inc()`, `diag_stat_inc_norecursion()`, `diag0c()`, `diag14()`, `diag204()`, and `diag210()`. `diag_map[]` maps statistic IDs to diagnose codes and names. `diag_amode31_ops` holds AMODE31 callable implementations. Debugfs `diag_stat` exposes per-CPU counters.

## Control Flow
Device init creates a read-only debugfs sequence file. Diagnose wrappers increment stats and tracepoints before issuing architecture-specific diagnose calls. `diag14()` translates virtual buffer addresses for subcodes that require it. `diag204()` validates vmalloc/page alignment, translates STIB4 addresses to physical page frame addresses, issues DIAG 204, and maps busy/unsupported return codes to errno. `diag210()` serializes access to a temporary AMODE31 buffer.

## State And Persistence
State includes per-CPU `diag_stat` counters and static AMODE31 temporary buffers for DIAG 210/8C paths. No persistent storage is used.

## Dependencies And Integration Points
Depends on debugfs, seq_file, tracepoints, AMODE31 sections, exception tables, vmalloc address helpers, and diagnose asm. It is shared by cpcmd, cert_store, diag310, diag324, and virtualization support.

## Risks And Edge Cases
Some diagnose calls require real/physical addresses, page alignment, or AMODE31 buffers. Incorrect translation can corrupt memory or fail silently. Statistic increments must avoid recursion in trace-sensitive contexts.

## Test Signals
Signals include debugfs `diag_stat` output, tracepoint events, DIAG 204 busy/unsupported tests, DIAG 210 serialization, and z/VM or LPAR feature smoke tests.
