# sources/compression/zstd/lib/common/portability_macros.h

## Purpose
`portability_macros.h` defines preprocessor-only feature and platform detection shared by C and assembly code. It intentionally contains no C declarations so assembly sources can include the same capability decisions.

## Important APIs, Types, and Functions
The header supplies fallback definitions for `__has_attribute`, `__has_builtin`, and `__has_feature`. It derives sanitizer flags `ZSTD_MEMORY_SANITIZER`, `ZSTD_ADDRESS_SANITIZER`, and `ZSTD_DATAFLOW_SANITIZER`, assembly symbol visibility through `ZSTD_HIDE_ASM_FUNCTION()`, CPU feature flags `STATIC_BMI2` and `DYNAMIC_BMI2`, assembly enablement flags `ZSTD_ASM_SUPPORTED` and `ZSTD_ENABLE_ASM_X86_64_BMI2`, CET marker `ZSTD_CET_ENDBRANCH`, and deterministic-build marker `ZSTD_IS_DETERMINISTIC_BUILD`.

## Control Flow, State, and Persistence
There is no runtime flow or state. The preprocessor evaluates compiler, OS, architecture, sanitizer, and build-option macros to choose whether BMI2 is assumed at compile time, dispatched at runtime, or unavailable; whether GAS-compatible assembly should be enabled; and whether assembly symbols need hidden/private annotations.

## Dependencies and Integration Points
This file is included from common compiler/CPU/assembly-adjacent code and must remain compatible with assemblers. `fse_decompress.c`, Huffman, and other hot paths depend on `DYNAMIC_BMI2`/`STATIC_BMI2` decisions for target attributes and runtime dispatch. Assembly implementations use `ZSTD_HIDE_ASM_FUNCTION()` and `ZSTD_CET_ENDBRANCH`, while release/reproducibility checks can inspect `ZSTD_IS_DETERMINISTIC_BUILD`.

## Risks and Test Signals
Risks are mostly build-matrix related: incorrectly enabling assembly under sanitizers can hide instrumentation, assuming BMI2 on unsupported targets can crash, and using C-only syntax would break assembly inclusion. Test signals include GCC, Clang, MSVC, Apple, Linux, and Windows builds; sanitizer builds confirming assembly disabled where required; x86-64 BMI2 dynamic and static builds; and reproducibility checks when macros that affect compressed output are toggled.
