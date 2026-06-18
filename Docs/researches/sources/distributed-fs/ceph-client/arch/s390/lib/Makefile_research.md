# sources/distributed-fs/ceph-client/arch/s390/lib/Makefile

## Purpose
Build manifest for s390-specific architecture library objects. It selects low-level helpers for delay, string/memory operations, user access, bit scanning, spinlocks, 128-bit shifts, checksums, probes, and optional architecture sanity tests.

## Important APIs, Types, And Functions
The Makefile adds core library objects through `lib-y` (`delay.o`, `string.o`, `uaccess.o`, `find.o`, `spinlock.o`, `tishift.o`, `csum-partial.o`) and `obj-y` (`mem.o`). Config-gated objects include `probes.o` for KPROBES/UPROBES, KUnit suites for kprobes, unwind, and module relocation sanity tests, `error-inject.o`, and `expoline.o`.

## Control Flow And State
Build-time control flow is purely Kconfig-driven. It disables KASAN instrumentation for `uaccess.o` because user-space access in different address spaces can trigger false positives. `test_kprobes_s390` is composed from assembly and C objects. `test_unwind.o` uses `-fno-optimize-sibling-calls` to preserve call-chain shape for unwinder tests.

## Dependencies And Integration
Integrates with the kernel build system, s390 arch Kconfig, KUnit, KASAN, kprobes/uprobe infrastructure, function error injection, and expoline mitigation configuration.

## Risks And Test Signals
Risks are missing objects under configuration combinations, accidental sanitizer instrumentation of uaccess, or compiler optimization breaking unwind tests. Signals include `allyesconfig`/`allmodconfig` builds, KUnit object linkage, and s390 defconfig builds with combinations of KPROBES, CMM, EXPOLINE_EXTERN, and selftest options.
