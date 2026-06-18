# sources/compression/zstd/contrib/linux-kernel/test/include/linux/kernel.h

Purpose: minimal `linux/kernel.h` shim providing alignment and warning macros for user-space kernel-zstd tests.

Important behavior: defines `WARN_ON(x)` as a no-op, `PTR_ALIGN(p,a)` using `ALIGN`, and `ALIGN`/`ALIGN_MASK` arithmetic macros for power-of-two alignment.

State, dependencies, and integration: no state or includes. It supports generated zstd code compiled outside the Linux kernel.

Risks and test signals: `WARN_ON` does not evaluate/report like the real kernel macro, so tests may miss warning-side effects. Alignment macros rely on `typeof`, so GCC/Clang extensions are required. Compile/runtime kernel tests are the signal.
