# sources/distributed-fs/ceph-client/lib/crc/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/Kconfig` declares build-time configuration for the kernel CRC library, including small CRC variants, CRC32, CRC64, architecture accelerations, KUnit tests, and benchmarks.

## Important APIs, Types, and Functions

Important symbols are `CRC4`, `CRC7`, `CRC8`, `CRC16`, `CRC_CCITT`, `CRC_ITU_T`, `CRC_T10DIF`, `CRC_T10DIF_ARCH`, `CRC32`, `CRC32_ARCH`, `CRC64`, `CRC64_ARCH`, `CRC_OPTIMIZATIONS`, `CRC_KUNIT_TEST`, `CRC_ENABLE_ALL_FOR_KUNIT`, and `CRC_BENCHMARK`.

## Control Flow

There is no runtime flow. Kconfig dependency resolution selects generic CRC objects and enables architecture-specific objects when both the base CRC and `CRC_OPTIMIZATIONS` are enabled and the architecture advertises support. KUnit options select the CRC variants needed by tests.

## State and Persistence Behavior

The file persists only build configuration state. Selected symbols determine which objects and architecture headers are compiled into the kernel or modules.

## Dependencies and Integration Points

The file integrates with `lib/crc/Makefile`, architecture feature symbols such as ARM/ARM64/PPC/RISCV/X86/S390/SPARC/LOONGARCH/MIPS, `KUNIT`, and `UML` exclusion for optimizations.

## Risks and Edge Cases

Incorrect defaults can compile unsupported instructions or miss optimized code. `CRC_OPTIMIZATIONS` disabled should fall back cleanly to generic implementations. KUnit select-all must not unintentionally affect production configs.

## Test Signals

Signals include randconfig/allmodconfig build coverage, architecture configs with and without optimization support, `CRC_OPTIMIZATIONS=n` fallback builds, KUnit enable-all coverage, and benchmark option dependency checks.

## Read Coverage

Source read size: 129 lines, 3437 bytes.
