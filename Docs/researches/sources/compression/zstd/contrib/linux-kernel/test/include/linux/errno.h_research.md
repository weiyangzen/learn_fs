# sources/compression/zstd/contrib/linux-kernel/test/include/linux/errno.h

Purpose: minimal `linux/errno.h` shim for the kernel zstd user-space tests.

Important behavior: defines only `EINVAL` as `22` under an include guard.

State, dependencies, and integration: no state and no includes. It satisfies generated code that needs invalid-argument error constants without pulling real kernel headers.

Risks and test signals: any generated source needing additional errno values will fail to compile until the shim is extended. The linux-kernel test target is the signal.
