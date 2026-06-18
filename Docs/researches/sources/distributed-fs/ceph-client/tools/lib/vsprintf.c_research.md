# sources/distributed-fs/ceph-client/tools/lib/vsprintf.c

Purpose: Provides userspace implementations of kernel-style `vscnprintf()`, `scnprintf()`, and `scnprintf_pad()` helpers.

Important APIs/types/functions: `vscnprintf(buf, size, fmt, args)` wraps `vsnprintf()` and returns the number actually written capped at `size - 1`. `scnprintf()` is variadic equivalent. `scnprintf_pad()` writes formatted text and pads the remaining buffer with spaces before NUL termination.

Control flow: Each function formats with `vsnprintf()`/`vscnprintf()`, compares the result against signed `size`, and returns a capped count. Padding loops from formatted length to `size`, fills spaces, then writes NUL.

State and persistence: Stateless except mutation of caller-provided buffers.

Dependencies/integration: Includes `<linux/kernel.h>`, `<sys/types.h>`, and `stdio.h` for `vsnprintf`; used by tools expecting kernel formatting semantics.

Risks: For `size == 0`, `ssize` is 0 and return expression can produce `-1`, matching kernel-ish semantics but risky for callers expecting nonnegative `int`. `scnprintf_pad()` writes `buf[i] = 0` after loop where `i == size`, which writes one byte past the supplied size if `i < size` branch runs to completion. Formatting errors from `vsnprintf()` are not specially handled.

Test signals: Test truncation, exact fit, zero size, formatting error if mockable, and `scnprintf_pad()` with small buffers under ASan to catch the apparent off-by-one write.
