# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memcpy-x86-64-asm-def.h

Purpose: defines the x86_64 memcpy benchmark implementation table through `MEMCPY_FN()` macro invocations.

Important APIs/types/functions: lists `memcpy_orig` as `x86-64-unrolled` and `__memcpy` as `x86-64-movsq`, both using `mem_alloc` and `mem_free`.

Control flow: preprocessor data only; behavior depends on how the includer defines `MEMCPY_FN`.

State and persistence: no runtime state.

Dependencies and integration: included once for prototypes and once for `struct function` table entries in `mem-functions.c`.

Risks: symbol names come from the included kernel assembly and must remain exported by the wrapper assembly file.

Test signals: function-help output lists both names, and both selected functions link and run.
