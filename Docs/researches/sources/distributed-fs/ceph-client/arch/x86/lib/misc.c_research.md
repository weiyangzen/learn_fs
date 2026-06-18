# sources/distributed-fs/ceph-client/arch/x86/lib/misc.c

Purpose: provides a small numeric formatting helper for counting decimal digits.

Important APIs/functions: defines `num_digits(int val)`.

Control flow: initializes digit count to one, adds one for a negative sign and negates the value, then multiplies a decimal threshold by 10 until the value is below the threshold. The result includes the sign when present.

State and persistence behavior: pure computation; no global state.

Dependencies/integration points: declared via `<asm/misc.h>` and used by x86 code needing decimal width estimates.

Risks: negating `INT_MIN` overflows in C, which is a latent edge-case risk unless callers avoid it or compiler behavior is tolerated. Uses `long long` threshold to avoid threshold overflow for normal int ranges.

Test signals: unit tests for 0, one-digit values, powers of ten, negative values, and `INT_MIN` behavior review.
