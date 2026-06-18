# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/adi-test.c

## Purpose
Functional selftest for the sparc64 privileged ADI driver exposed as `/dev/adi`. It verifies ADI version tag read/write and seek behavior over physical memory tag offsets.

## Important APIs, types, and functions
Helpers include debug/stat collection (`debug_print()`, `update_stats()`, `print_stats()`), `/proc/iomem` parsing in `build_memory_map()`, timing with `RDTICK`, IO wrappers `read_adi()`, `pread_adi()`, `write_adi()`, `pwrite_adi()`, `seek_adi()`, random tag generation via tick modulo 16, and eight test functions stored in `tests[]`.

## Control flow
`main()` builds a RAM range map, opens `/dev/adi`, then runs each test and reports pass/fail through kselftest. Tests write random ADI version bytes at offsets derived from physical addresses divided by `ADI_BLKSZ`, then read back and compare. Coverage includes aligned one-byte, 4096-byte, 10327-byte, unaligned 12541-byte, lseek semantics, and read/write variants for one byte, 9434 bytes, and 14963 bytes.

## State and persistence
Global RAM range arrays capture up to five System RAM ranges from `/proc/iomem`. Stats accumulate syscall counts, total tick measurements, and bytes. ADI version tags are written through `/dev/adi` to system state but are test-scoped.

## Dependencies and integration points
Requires sparc64 ADI support, `/dev/adi`, readable `/proc/iomem`, and kselftest helpers. `drivers_test.sh` handles module loading before invoking it.

## Risks
`MAX_RANGES_SUPPORTED` is fixed at five with no visible bounds check while parsing `/proc/iomem`. Partial read/write wrappers loop until full size but do not handle zero-length progress. Tests choose physical offsets near RAM range starts/ends and assume they are valid for ADI driver operations.

## Test signals
Each test emits kselftest pass/fail. Final process exits fail if any test failed, otherwise exits pass. Debug stats can be printed when debug bits are enabled.
