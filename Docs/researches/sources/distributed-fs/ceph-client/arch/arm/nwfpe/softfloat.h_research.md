# sources/distributed-fs/ceph-client/arch/arm/nwfpe/softfloat.h

Purpose: Declares the NWFPE SoftFloat ABI for ARM kernel floating-point emulation. It defines software float storage types, rounding and exception constants, optional extended precision support, and prototypes for conversions, arithmetic, comparisons, and NaN helpers.

Important APIs and types: `float32` is `u32`, `float64` is `u64`, and `floatx80` is a packed/aligned struct with endian-sensitive high-word placement. `FLOATX80` is enabled by `CONFIG_FPE_NWFPE_XP`. The header declares `float_detect_tininess`, `float_round_*` modes, and FPA11-ordered exception flags (`invalid`, `divbyzero`, `overflow`, `underflow`, `inexact`). Public prototypes include `float32_add/sub/mul/div/rem/sqrt`, equivalent double and optional extended operations, conversions to/from `int32`, and comparison variants.

Control flow and inline behavior: The header supplies fast inline sign extraction and no-NaN comparison helpers (`float32_eq_nocheck`, `float32_lt_nocheck`, `float64_eq_nocheck`, `float64_lt_nocheck`) that assume callers have already handled NaNs. These helpers preserve signed-zero equality and implement sign-aware ordering through integer comparisons.

State and dependencies: The header depends on NWFPE typedefs such as `flag`, `bits32`, and `bits64` from surrounding includes. Exception state is represented externally through `float_raise()` and `struct roundingData` pointers used by implementation functions; the struct itself is defined outside this header. Endianness of `floatx80` is explicitly ABI-relevant.

Integration points: Consumed by NWFPE execution code and implemented by `softfloat.c` plus specialize/macro includes. The exception flag order is intentionally matched to FPA11 rather than the original SoftFloat order, which matters for emulator status-register integration.

Risks: Because `struct roundingData` is only forward-referenced, include ordering must ensure its complete definition is visible where needed. `floatx80` packing/alignment and `__ARMEB__` layout are ABI-sensitive. The no-check comparison helpers are unsafe if used with NaNs. Tests should compile all consumers under little-endian, big-endian, and `CONFIG_FPE_NWFPE_XP` variants where available.
