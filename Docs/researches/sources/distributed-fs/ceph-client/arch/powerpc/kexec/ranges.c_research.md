# sources/distributed-fs/ceph-client/arch/powerpc/kexec/ranges.c

## Purpose
Builds and edits PowerPC kexec/kdump physical memory range lists. The code is shared between `CONFIG_KEXEC_FILE` load-time segment placement and `CONFIG_CRASH_DUMP` crash-memory export paths, producing lists for reserved ranges, excluded ranges, usable kdump ranges, crash ELF core ranges, and explicit removals.

## Important APIs, Types, And Functions
The core type is `struct crash_mem`, with `struct range` entries stored as inclusive `[start,end]` spans. Generic helpers are `realloc_mem_ranges`, `add_mem_range`, and `sort_memory_ranges`; private helpers include `__add_mem_range`, `__merge_memory_ranges`, and `rngcmp`. Kexec-file range population is handled by `get_reserved_memory_ranges` and `get_exclude_memory_ranges`, which pull RTAS, OPAL, TCE table, retained initrd, kernel image, hash table, and firmware `/reserved-ranges` data. Crash-dump paths include `get_usable_memory_ranges`, `get_crash_memory_ranges`, `crash_exclude_mem_range_guarded`, and `remove_mem_range`.

## Control Flow
Range insertion grows the crash-memory array in `MEM_RANGE_CHUNK_SZ` chunks, appends inclusive ranges, and optionally sorts and merges adjacent spans. Kexec-file exclusion first adds device-tree and platform-reserved areas, then sorts and merges to make later segment placement checks cheap. Crash memory collection walks `memblock` memory, skips the backup source area, excludes the crashkernel and crashk CMA ranges with guarded reallocation, appends RTAS/OPAL and the backup source header, and finally sorts without merging so ELF program headers remain distinct where required.

## State And Persistence
All state is transient kernel memory owned by the caller through `struct crash_mem **`. The code reads persistent boot/runtime state from the device tree, `saved_command_line`, `crashk_res`, `crashk_cma_ranges`, `htab_address`, `htab_size_bytes`, and memblock, but does not persist changes itself. Firmware-provided reserved ranges and platform structures become copied into range arrays used by later kexec or kdump code.

## Dependencies And Integration Points
Depends on Linux kexec, crash core, memblock, Open Firmware helpers, kernel section symbols, PPC64 crashdump constants, and optional hash-MMU globals. It integrates with `kexec_file_load` placement, crash dump ELF core generation, crashkernel reservation, RTAS/OPAL firmware data, TCE tables, and kexec-tools compatibility expectations.

## Risks And Edge Cases
Inclusive end arithmetic can overflow if callers pass extreme base/size pairs. `add_mem_range` only updates the first overlapping range and relies on later sort/merge for full canonicalization. The source snapshot contains a duplicated local declaration in `crash_exclude_mem_range_guarded`, which is a compile-time risk if present in the active tree. Device-tree properties may be absent, malformed, or partially read; `add_tce_mem_ranges` tolerates missing TCE properties but aborts other read errors. Crash range splitting requires enough spare capacity before calling `crash_exclude_mem_range`, hence the guarded reallocation.

## Test Signals
Useful coverage is `kexec_file_load` on pseries and powernv, kdump boot with crashk CMA ranges, retained-initrd loads, hash-MMU and radix-MMU builds, and device trees with RTAS, OPAL, TCE, and `/reserved-ranges`. Unit-style tests should stress adjacent range merging, exact removal, edge trimming, middle splitting, backup source handling, and full-array reallocation.
