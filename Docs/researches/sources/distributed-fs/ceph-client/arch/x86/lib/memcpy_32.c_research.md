# sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_32.c

Purpose: provides exported 32-bit C wrappers for `memcpy` and `memset` when compiler builtins call out-of-line functions.

Important APIs/functions: defines `memcpy()` and `memset()` as visible functions, exporting both. They delegate to `__memcpy` and `__memset`.

Control flow: direct wrapper calls only: `memcpy(to, from, n)` returns `__memcpy(to, from, n)`, and `memset(s, c, count)` returns `__memset(s, c, count)`.

State and persistence behavior: state effects are entirely those of the underlying memory functions. No local globals.

Dependencies/integration points: 32-bit x86 library build, generic string/memory implementations providing `__memcpy` and `__memset`, compiler out-of-line builtin calls, and module symbol exports.

Risks: wrapper symbols must avoid macro/builtin substitution, hence `#undef`. Missing exports can break modules or compiler-emitted calls. Correctness depends on underlying implementations.

Test signals: 32-bit build/link tests, module use of `memcpy`/`memset`, compiler configurations that emit out-of-line calls, and basic memory operation tests.
