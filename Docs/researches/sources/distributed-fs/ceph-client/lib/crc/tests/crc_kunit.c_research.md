# sources/distributed-fs/ceph-client/lib/crc/tests/crc_kunit.c

## Purpose
This file provides generic KUnit tests and optional benchmarks for CRC library functions, including CRC7, CRC16, T10DIF, CRC32, CRC32C, CRC64 BE, and CRC64 NVMe.

## Important APIs, Types, and Functions
Important state and types include `struct crc_variant`, global PRNG state `rng`, `test_buffer`, and `test_buflen`. Key helpers are `crc_ref()`, `crc_suite_init()`, `crc_suite_exit()`, `generate_random_initial_crc()`, `generate_random_length()`, `crc_interrupt_context_test()`, `crc_test()`, and `crc_benchmark()`. Wrapper functions adapt public CRC APIs to the uniform `u64 (*)(u64,const u8*,size_t)` signature.

## Control Flow
Suite init allocates a page-rounded vmalloc buffer so overreads hit a guard page, seeds deterministic random data, and each enabled CRC variant runs 1000 randomized tests. Each test picks an initial CRC, random length, and random offset, sometimes placing the input adjacent to the guard page, then compares the implementation to a bit-at-a-time reference. It also runs concurrent task/softirq/hardirq context checks. Benchmarks run only under `CONFIG_CRC_BENCHMARK`.

## State and Persistence
The buffer and PRNG state live for the suite lifetime and are released in suite exit. No persistent data is written.

## Dependencies and Integration Points
It depends on KUnit, `kunit_run_irq_test()`, Linux CRC headers, PRNG, vmalloc, and optional CRC Kconfig symbols. It is the main cross-arch signal for the accelerated implementations in this subset.

## Risks and Test Signals
Risks include the reference implementation itself being wrong for a variant convention, deterministic random coverage missing specific thresholds, and benchmark code perturbing timing. Its strongest signals are guard-page tail tests, random alignment/length coverage, and interrupt-context validation for SIMD/FPU-safe accelerated code.
