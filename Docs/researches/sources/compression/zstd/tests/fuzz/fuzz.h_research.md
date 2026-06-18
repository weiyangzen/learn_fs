# sources/compression/zstd/tests/fuzz/fuzz.h

## Purpose
`fuzz.h` declares the common libFuzzer entrypoint signature used by the regression driver and fuzz target build.

## APIs and integration
It includes standard integer/size types and declares `int LLVMFuzzerTestOneInput(const uint8_t *src, size_t size);`. Each fuzz target defines this function, while `regression_driver.c` or libFuzzer provides the caller.

## State, dependencies, risks, and test signals
The header contains no state. Its main dependency is signature compatibility with libFuzzer. Any mismatch would fail to link or prevent regression-driver execution.
