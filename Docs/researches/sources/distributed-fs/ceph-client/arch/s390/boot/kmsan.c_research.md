<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c

Purpose: Supplies a boot-time stub for `kmsan_unpoison_memory()` so code shared with instrumented kernel paths can link in the s390 boot environment.

Important APIs/types/functions: Defines `void kmsan_unpoison_memory(const void *address, size_t size)` as an empty function after including `linux/kmsan-checks.h`.

Control flow: Calls to `kmsan_unpoison_memory()` during decompressor execution are no-ops. There is no branching or side effect.

State and persistence: No state is read or written.

Dependencies and integration points: Exists because boot code may include or call APIs that are normally provided by KMSAN infrastructure, while the decompressor has no full sanitizer runtime. It complements `string.c`, which explicitly undefines KASAN/KMSAN before including shared string code.

Risks: This intentionally drops KMSAN semantics in early boot. If future boot code relies on unpoisoning for correctness rather than sanitizer bookkeeping, this stub would hide the mismatch.

Test signals: KMSAN-enabled s390 builds, decompressor link tests, and boot tests with memory instrumentation options enabled.

Source read size: 6 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/kmsan.c -->
