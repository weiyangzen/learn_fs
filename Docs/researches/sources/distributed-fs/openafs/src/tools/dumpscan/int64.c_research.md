# sources/distributed-fs/openafs/src/tools/dumpscan/int64.c

Purpose: formatting, shifting, and optional self-tests for `dt_uint64`, supporting both native 64-bit and emulated `{hi,lo}` implementations from `intNN.h`.

Important APIs/functions: `hexify_int64` returns a fixed-width 16-hex-digit string. `decimate_int64` formats decimal; the non-native path uses a precomputed table of decimal powers of two and digit accumulation. `shift_int64` shifts left or right across the high/low boundary. Under `TEST_INT64`, `verify_int64_size`, constructor/comparison tests, and a test `main` are compiled.

State/dependencies: uses static buffers when callers pass `NULL`, so results are overwritten by later calls. Non-native decimal formatting mutates `bitvals` from ASCII digits to numeric digits in `prep_table`. Dependencies are `intNN.h` macros and stdio/string.

Risks/test signals: static return buffers are not thread-safe and nested calls need caller-provided buffers. Shift expressions around 32-bit boundaries are delicate. The optional test block provides constructor and comparison coverage but says arithmetic tests are missing.
