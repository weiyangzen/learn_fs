# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/octeon-memcpy.S

Purpose: provides an Octeon-tuned unified assembly implementation of `memcpy`, `memmove`, `__raw_copy_from_user`, and `__raw_copy_to_user` for 64-bit MIPS. It optimizes common aligned and unaligned copy paths while preserving user-copy exception semantics.

Important APIs and labels: exported symbols are `memcpy`, `memmove`, `__raw_copy_from_user`, and `__raw_copy_to_user`. Internal labels include `__memcpy`, `src_unaligned`, `copy_bytes`, `l_exc`, `l_exc_copy`, store exception fixups (`s_exc_p*`), and reverse-copy `__rmemcpy`. The `EXC()` macro emits exception-table entries for faultable loads and stores.

Control flow: `memcpy` returns the original destination in `v0` and falls into the shared copy engine. The engine prefetches for large copies, handles aligned 16-word, 8-word, 4-word, word, and byte tails, and has a separate unaligned-source path using MIPS left/right load instructions. User-copy failures enter exception handlers that compute remaining byte count in `len`; load failures copy known-good bytes first to avoid leaking stale destination data to user space. `memmove` checks overlap and either delegates to forward `__memcpy` or performs byte-wise reverse/upward copying.

State and persistence: no persistent state. Correctness depends on register conventions: `dst`, `src`, `len`, and `AT` must retain meanings described in the header comments, especially for user-copy exception recovery.

Dependencies and integration points: depends on MIPS ABI register definitions, exception table format, thread `THREAD_BUADDR`, and uaccess calling conventions. It overrides core memory primitives for Octeon builds and is referenced by optional L2 locking in Octeon setup.

Risks: the assembly is sensitive to delay slots, endianness macros, register clobbers, and exception-table target accuracy. Any change that updates `src` and `dst` asymmetrically can break the load-exception invariant and leak kernel data on copy-from-user faults. `memmove` reverse path is intentionally simple, so performance differs from forward copy for overlap.

Test signals: kernel selftests or boot smoke tests should cover aligned and unaligned copies, short lengths, long lengths over prefetch thresholds, overlap cases for `memmove`, and fault-injection/usercopy tests that verify the returned uncopied length and destination clearing behavior.
