# sources/compression/zstd/contrib/linux-kernel/test/include/linux/types.h

Purpose: minimal Linux types shim for user-space compilation of generated kernel zstd sources.

Important behavior: includes `<stddef.h>` and `<stdint.h>` under an include guard, providing `size_t`, `ptrdiff_t`, and fixed-width integer types used by the generated sources.

State, dependencies, and integration: no state. It is a foundational shim included by other fake Linux headers and generated zstd code.

Risks and test signals: real kernel-specific aliases are absent; current generated zstd code uses standard fixed-width types. Compile failures indicate the shim needs to grow.
