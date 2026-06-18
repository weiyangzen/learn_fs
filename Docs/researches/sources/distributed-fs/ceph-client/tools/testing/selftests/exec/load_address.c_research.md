# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/load_address.c

## Purpose
Validates that PIE and static PIE executables are loaded at addresses aligned to the maximum PT_LOAD segment alignment requested by linker `-z max-page-size`.

## Important APIs, Types, And Functions
Uses `dl_iterate_phdr()` with callback `ExtractStatistics()`, `struct dl_phdr_info`, `PT_LOAD`, `PT_INTERP`, `/proc/self/maps`, and kselftest result helpers. Local `struct Statistics` records load address, alignment, and interpreter presence.

## Control Flow
The program prints `/proc/self/maps`, walks only the main executable program headers, records maximum PT_LOAD alignment and whether `PT_INTERP` exists, infers whether interpreter is expected from `argv[0]` containing `.static.`, and emits four results: interpreter presence, alignment found, alignment power-of-two, and load address alignment.

## State And Persistence
No persistent state; reads its own maps and program headers.

## Dependencies And Integration Points
Built into several variants by the Makefile with different max-page-size values and static/dynamic PIE modes.

## Risks
Toolchain/linker behavior determines PT_LOAD alignment. The callback ignores shared library headers by checking `dlpi_name`, which depends on loader reporting conventions.

## Test Signals
Four kselftest results per binary show expected interpreter, nonzero alignment, power-of-two alignment, and zero load-address misalignment.
