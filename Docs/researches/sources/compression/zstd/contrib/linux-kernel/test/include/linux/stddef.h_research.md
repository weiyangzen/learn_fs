# sources/compression/zstd/contrib/linux-kernel/test/include/linux/stddef.h

Purpose: shim mapping `linux/stddef.h` to standard C `stddef.h` for user-space tests.

Important behavior: include guard plus `#include <stddef.h>`.

State, dependencies, and integration: no state. It supplies size and null-related definitions required after include rewriting.

Risks and test signals: standard C definitions are sufficient for current generated zstd code. Missing kernel-specific typedefs/macros would show up as compile failures.
