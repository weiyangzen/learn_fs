## sources/distributed-fs/openafs/src/external/c-tap-harness/tests/tap/macros.h

Purpose: portability macro header shared by TAP C headers. It abstracts compiler attributes, unused-parameter annotations, and C++ linkage wrappers.

Important APIs/macros: fallback definition for `__attribute__`, conditional fallback for `__alloc_size__`, fallback for `__warn_unused_result__`, Clang/LLVM diagnostic suppression for unknown attributes, `UNUSED`, `BEGIN_DECLS`, and `END_DECLS`.

Control flow: preprocessor-only logic selects fallbacks based on GCC/Clang/MS-style feature macros. No runtime behavior.

State and persistence: no runtime state.

Dependencies: compiler predefined macros such as `__GNUC__`, `__GNUC_MINOR__`, `__clang__`, `__llvm__`, and `__cplusplus`.

Integration points: included by `basic.h`, `float.h`, and likely other TAP add-ons so public headers can use GCC-style attributes without breaking older compilers or C++ consumers.

Risks: `#pragma GCC diagnostic ignored "-Wattributes"` affects the whole compilation context after inclusion on Clang/LLVM. The feature tests are intentionally broad and may not model every compiler claiming GCC compatibility. Redefining `__attribute__` is common in portable C but can interact poorly with other portability layers if include order differs.

Test signals: compile matrix across old GCC-like, Clang, strict C, and C++ modes; verify public headers remain parsable and format attributes still work when supported.
