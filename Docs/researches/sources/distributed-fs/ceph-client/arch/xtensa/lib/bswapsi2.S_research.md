# sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapsi2.S

Purpose: Implements exported 32-bit byte swap helper `__bswapsi2`.

Important APIs, types, and functions: `__bswapsi2`, `ssai`, `srli`, `src`, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Uses shift/merge instructions to reverse the four bytes in `a2` and returns the result in `a2`.

State and persistence: Register-only helper.

Dependencies and integration: Supports compiler-generated `bswap32` operations and kernel byteorder helpers.

Risks: Incorrect byte ordering would corrupt protocol and disk metadata conversions; otherwise the routine is small and deterministic.

Test signals: `__builtin_bswap32` and byteorder tests with asymmetric values such as `0x01234567`.
