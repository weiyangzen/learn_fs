# sources/compression/xz/cmake/tuklib_integer.cmake

## Purpose
This module configures integer portability and optimization macros: endianness, byte swapping, fast unaligned access, unsafe type punning, and compiler alignment intrinsics.

## Important APIs and Control Flow
`tuklib_integer_internal_strict_align(OBJDUMP_REGEX)` compiles a static-library probe, disassembles it with `CMAKE_OBJDUMP`, and infers strict alignment from byte-load instruction patterns. `tuklib_integer(TARGET_OR_ALL)` uses `test_big_endian`, checks builtin byte-swap support or headers like `byteswap.h`, `sys/endian.h`, and `sys/byteorder.h`, then estimates `TUKLIB_FAST_UNALIGNED_ACCESS` from processor names and compiler macros for x86, PowerPC, ARM, ARM64, RISC-V, and LoongArch. It also exposes `TUKLIB_USE_UNSAFE_TYPE_PUNNING` and checks `__builtin_assume_aligned`.

## State, Dependencies, and Integration
It mutates target/global definitions and CMake cache options. Dependencies are CMake check modules, an object dump tool, and compile probes. It feeds low-level integer access code in tuklib and liblzma hot paths.

## Risks and Test Signals
This is performance- and correctness-sensitive: wrong unaligned-access detection can cause crashes or slow code. The ARM64/GCC and LoongArch heuristic paths are especially subtle. Cross-architecture CI, including ARM runners/MSYS2 ARM, helps validate assumptions.
