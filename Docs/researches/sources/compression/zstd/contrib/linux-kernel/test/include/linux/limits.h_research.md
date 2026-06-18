# sources/compression/zstd/contrib/linux-kernel/test/include/linux/limits.h

Purpose: shim mapping `linux/limits.h` to the host C library limits for user-space kernel-zstd tests.

Important behavior: include guard plus `#include <limits.h>`.

State, dependencies, and integration: no state. It satisfies include rewrites performed by the freestanding generator.

Risks and test signals: host libc limits may not perfectly match kernel limits, but zstd's generated code primarily needs numeric bounds. Compile failures or behavioral test failures indicate missing compatibility.
