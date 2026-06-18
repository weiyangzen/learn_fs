# sources/compression/zstd/contrib/linux-kernel/test/include/linux/compiler.h

Purpose: minimal user-space shim for Linux compiler annotations needed by the kernel zstd test harness.

Important behavior: defines `inline` as `__inline __attribute__((unused))` if absent, `noinline` as `__attribute__((noinline))`, and `fallthrough` as GCC's fallthrough attribute.

State, dependencies, and integration: no state and no external includes. It is included indirectly by generated kernel zstd files through `linux/compiler.h` when compiling outside a real kernel tree.

Risks and test signals: only covers the annotations currently needed by the generated sources. Missing future compiler macros will surface as linux-kernel test compile failures.
