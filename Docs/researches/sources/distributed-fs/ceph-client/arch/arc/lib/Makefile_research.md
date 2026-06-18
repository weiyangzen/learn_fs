# sources/distributed-fs/ceph-client/arch/arc/lib/Makefile

Purpose: selects ARC assembly implementations for core string and memory primitives.

Important entries: always builds ARC700-compatible `strchr-700.o`, `strcpy-700.o`, `strlen.o`, and `memcmp.o`. ARCompact adds `memcpy-700.o`, `memset.o`, and `strcmp.o`. ARCv2 adds `memset-archs.o` and `strcmp-archs.o`, plus either `memcpy-archs-unaligned.o` or `memcpy-archs.o` depending on `CONFIG_ARC_USE_UNALIGNED_MEM_ACCESS`.

Control flow: build-time selection only; object choice determines which exported C library symbols satisfy kernel calls.

State and persistence: no runtime state.

Dependencies and integration: integrates with kernel lib symbol resolution and ISA configuration. The selected files must match CPU alignment capabilities, zero-overhead-loop behavior, endian support, and optional 64-bit load/store support.

Risks: wrong object selection can cause illegal instructions or bad alignment behavior on a target CPU. Because these routines implement ubiquitous primitives, defects have whole-kernel blast radius.

Test signals: architecture builds for ARCompact/ARCv2, boot smoke tests, string/memory KUnit or lib tests, unaligned-copy stress, and endian build coverage.
