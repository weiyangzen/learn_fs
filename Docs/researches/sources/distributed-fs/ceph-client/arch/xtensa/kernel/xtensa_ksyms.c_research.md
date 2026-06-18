# sources/distributed-fs/ceph-client/arch/xtensa/kernel/xtensa_ksyms.c

Purpose: Exports small Xtensa atomic helper symbols used by compiler-generated code or modules.

Important APIs, types, and functions: `__sync_fetch_and_and_4()` and `__sync_fetch_and_or_4()`, both exported with `EXPORT_SYMBOL`.

Control flow: Each helper casts the pointer to `atomic_t *` and delegates to `atomic_fetch_and()` or `atomic_fetch_or()`, returning the previous value to match GCC `__sync_fetch_and_*` semantics.

State and persistence: Mutates the 32-bit memory word addressed by the caller atomically; no internal state is maintained.

Dependencies and integration: Depends on Linux atomic primitives and module symbol export. Complements Xtensa toolchain code generation for configurations where libgcc-style atomic builtins may be emitted.

Risks: Only 32-bit `and` and `or` helpers are provided here; callers must pass properly aligned atomic-compatible storage. Type punning assumes Linux atomic layout matches an unsigned int word.

Test signals: Module build/load using GCC sync builtins, atomic operation litmus tests, and modpost symbol resolution.
