# sources/compression/zstd/contrib/linux-kernel/test/include/linux/math64.h

Purpose: minimal `linux/math64.h` shim for user-space kernel-zstd tests.

Important behavior: defines `div_u64(dividend, divisor)` as plain C division.

State, dependencies, and integration: no state and no includes. It provides the one 64-bit division helper needed by generated code in the test environment.

Risks and test signals: real kernel helpers handle architecture-specific details; this shim assumes host C supports the division directly. Additional math64 needs will surface during linux-kernel test compilation.
