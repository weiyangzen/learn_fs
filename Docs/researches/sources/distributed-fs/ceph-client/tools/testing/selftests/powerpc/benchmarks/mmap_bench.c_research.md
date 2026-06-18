# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/mmap_bench.c

## Purpose
Benchmarks mmap/munmap or page-fault behavior over a large anonymous mapping.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `MEMSIZE`, `PAGE_SIZE`, `CHUNK_COUNT`, `usage()`, `test_mmap()`, and `main()` with an option to select faulting behavior.

## Control Flow
The benchmark maps memory, optionally touches one byte per chunk/page to fault it in, unmaps it, repeats for many iterations, and prints elapsed time via timebase helpers.

## State and Persistence
Process-local virtual memory mappings are repeatedly created and destroyed; no files are persisted.

## Dependencies and Integration Points
Depends on anonymous mmap, system page behavior, `getopt`, and PowerPC utility timing.

## Risks and Test Signals
Risks include memory pressure, assumptions about 64 KiB pages in constants, and benchmark variability. Failures are mmap/munmap errors or harness failures.
