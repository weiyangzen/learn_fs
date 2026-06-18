## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/float.c

Purpose: optional TAP helper implementation for floating-point comparisons, separated from `basic.c` so projects only need math-library linkage when they use it.

Important APIs/types/functions: `is_double(double left, double right, double epsilon, const char *format, ...)` compares doubles and reports through `okv()`; static `is_equal_infinity()` detects matching signed infinities without relying on `isinf()` sign values.

Control flow: `is_double()` starts a `va_list`, flushes stderr, treats two NaNs as equal, treats equal-signed infinities as equal, otherwise checks `fabs(left - right) <= epsilon`. On failure it prints left/right diagnostics before delegating the failing TAP line to `okv()`.

State and persistence: no persistent or static mutable state. It mutates only the global TAP state inside `okv()` and diagnostic output in `basic.c`.

Dependencies: `<math.h>` for `isnan`, `isinf`, and `fabs`; `<stdarg.h>`/`stdio`; `tests/tap/basic.h` and `tests/tap/float.h`. Defines `_XOPEN_SOURCE 600` in strict/PEDANTIC builds for math macros. Clang warning pragmas suppress known conversion noise around floating macros.

Integration points: linked into tests that need floating comparisons. It relies on `basic.c` for numbering, diagnostics, and TAP output.

Risks: epsilon is caller-provided and no guard prevents a negative epsilon, which would only pass NaN/infinity cases or exact differences satisfying the negative comparison impossibly. Treating NaNs as equal is a test-helper policy choice, not IEEE equality. Requires math support that may need `-lm`.

Test signals: validate equal finite values, within/outside epsilon, positive vs negative infinity, two NaNs, one NaN, negative epsilon behavior, and formatted descriptions propagated through `okv()`.
