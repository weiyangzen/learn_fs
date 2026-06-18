# sources/distributed-fs/ceph-client/arch/parisc/lib/ucmpdi2.c

Purpose: implements the libgcc helper `__ucmpdi2()` for unsigned 64-bit comparison on PA-RISC configurations where the compiler may emit calls instead of inline code.

Important APIs/types/functions: `union ull_union` overlays an `unsigned long long` with two 32-bit words named `high` and `low`. `word_type __ucmpdi2(unsigned long long a, unsigned long long b)` returns libgcc comparison codes: `0` when `a < b`, `1` when equal, and `2` when `a > b`.

Control flow: both inputs are split into high and low words. The function compares high words first and returns immediately on a difference; low words are compared only when high words match. Equality returns `1`.

State and dependencies: no state or persistence. Depends on `linux/libgcc.h` for `word_type` and on the architecture's word ordering matching the union field interpretation used here.

Risks: the union layout is endian-sensitive. It is correct only if `ui.high` maps to the most significant 32 bits for the target ABI. Because this is a compiler helper, any ABI mismatch can surface as broad arithmetic misbehavior rather than a local failure.

Test signals: compiler-generated 64-bit unsigned comparison tests, libgcc helper ABI tests, both endian/ABI build coverage for PA-RISC, and kernel code paths that compare `u64` values on 32-bit builds.
