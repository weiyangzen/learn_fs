<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/helpers.h -->
# sources/distributed-fs/ceph-client/include/vdso/helpers.h

Purpose: provides sequence-counter and memory-ordering helpers for safe lockless kernel writes and userspace vDSO reads of VVAR clock data, including time namespace detection.

Important APIs and types: helpers include `vdso_is_timens_clock`, `vdso_read_begin`, `vdso_read_begin_timens`, `vdso_read_retry`, `vdso_write_seq_begin`, `vdso_write_seq_end`, `vdso_write_begin_clock`, `vdso_write_end_clock`, `vdso_write_begin`, and `vdso_write_end`.

Control flow: writers mark seq odd, issue write barriers, update clock fields, issue another barrier, then mark seq even. Readers spin while seq is odd, use read barriers around data loads, and retry if the sequence changed. Time namespace pages use an odd seq with `VDSO_CLOCKMODE_TIMENS` to force a special slow path.

State and persistence: no owned state; helpers operate on `vdso_clock.seq` fields in shared VVAR pages.

Dependencies and integration points: depends on asm barriers, datapage, processor relax, and clocksource mode definitions. It integrates with kernel timekeeping writers and generic vDSO clock readers.

Risks and test signals: high risks are missing barriers, compiler tearing without `READ_ONCE`/`WRITE_ONCE`, infinite spin on time namespace pages, and updating only one clock slot. Test concurrent time updates, time namespace clocks, weak-memory architectures, and lockless reader retry rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/helpers.h -->
