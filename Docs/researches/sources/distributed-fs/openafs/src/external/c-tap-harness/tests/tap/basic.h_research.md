## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/basic.h

Purpose: public header for the C TAP basic helper library. It defines declarations, utility macros, compiler attributes, and callback types used by C tests and add-on TAP helpers.

Important APIs/types/functions: exposes `extern unsigned long testnum`, planning APIs (`plan`, `plan_lazy`, `skip_all`), reporting APIs (`ok`, `okv`, `skip`, `ok_block`, `skip_block`), comparison helpers (`is_bool`, `is_int`, `is_string`, `is_hex`, `is_blob`), bailout/diagnostic helpers, diagnostic-file add/remove functions, allocation wrappers, source/build file lookup, temporary directory helpers, and cleanup registration callbacks. Defines `ARRAY_SIZE`, `ARRAY_END`, `bcalloc_type`, and `breallocarray_type`.

Control flow: no executable control flow, but the API contract implies tests call `plan()` or `plan_lazy()` before assertions and may register cleanup functions that run from the implementation's `atexit()` handler.

State and persistence: declares the globally visible `testnum`; the rest of state lives in `basic.c`. Temporary directories and diagnostic files are represented through implementation-owned heap allocations returned to callers for explicit freeing.

Dependencies: includes `<stdarg.h>`, `<stddef.h>`, and `tests/tap/macros.h` for portability attributes and C++ linkage wrappers.

Integration points: this is the include surface for test code. Attribute annotations enable printf-format checking, malloc/alloc-size hints, nonnull checks, and noreturn diagnostics on supporting compilers while remaining portable through macro fallbacks.

Risks: exposes mutable `testnum`, so tests can manually alter numbering. The comment notes `test_cleanup_register()` is a backward-compatible API mistake and the data-bearing variant is preferred. Attribute portability depends on the fallbacks in `macros.h`.

Test signals: compile tests should verify the header works from C and C++, preserves format warnings on GCC/Clang, and that each declaration links against `basic.c`.
