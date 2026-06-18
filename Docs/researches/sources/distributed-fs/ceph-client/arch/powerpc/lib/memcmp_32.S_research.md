# sources/distributed-fs/ceph-client/arch/powerpc/lib/memcmp_32.S

This file exports the 32-bit PowerPC `memcmp` implementation. It compares two buffers in `r3` and `r4` for `r5` bytes and returns zero, positive, or negative according to the first differing byte/word ordering expected by the C library-style kernel ABI.

Control flow divides the length by four and performs a word loop with indexed `lwzx` loads. If a word differs, it returns `1` or `-1` based on unsigned word comparison rather than subtracting the whole word. If all full words match, it checks remaining two-byte and one-byte tails. The halfword and byte tails subtract the second value from the first to produce an exact signed difference for small tails.

State is register-only. Dependencies are the PowerPC 32-bit calling convention and `EXPORT_SYMBOL(memcmp)` for kernel users. The implementation assumes regular kernel addresses and has no exception table because `memcmp` is not a uaccess primitive. Risks include endian-sensitive semantics for word-level early differences: returning only sign is acceptable for `memcmp`, but the sign must match the first byte difference under the architecture's load ordering. Test signals include lib/string tests, crypto and filesystem comparison workloads, and randomized comparison against generic C `memcmp`.
