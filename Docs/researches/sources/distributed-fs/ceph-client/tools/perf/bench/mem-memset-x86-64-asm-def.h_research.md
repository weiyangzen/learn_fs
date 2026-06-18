# Research: sources/distributed-fs/ceph-client/tools/perf/bench/mem-memset-x86-64-asm-def.h

Purpose: defines the x86_64 memset benchmark implementation table through `MEMSET_FN()` macro invocations.

Important APIs/types/functions: lists `memset_orig` as `x86-64-unrolled` and `__memset` as `x86-64-stosq`, both using `mem_alloc` and `mem_free`.

Control flow: preprocessor data only; expansion depends on includer macro.

State and persistence: no state.

Dependencies and integration: included for prototypes and function table construction in `mem-functions.c`.

Risks: description says movsq for a memset `stosq` variant; labels should remain clear for users. Symbol names must match wrapper assembly exports.

Test signals: function-help output and selected execution of both x86 memset implementations.
