<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hash.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/hash.h

## Purpose
`hash.h` provides fast integer and pointer hash helpers for kernel-derived user-space tools.

## APIs And Flow
The main APIs are `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `GOLDEN_RATIO_PRIME`, `__hash_32_generic()`, `hash_32()`, `hash_64_generic()`, `hash_long()`, `hash_ptr()`, and `hash32_ptr()`. Flow is purely inline: values are multiplied by golden-ratio constants and high bits are selected according to the requested bucket bit count; 64-bit inputs fall back to folded 32-bit hashing on 32-bit hosts.

## State, Dependencies, Risks, Tests
There is no persistent state. It depends on `asm/types.h`, `linux/compiler.h`, `BITS_PER_LONG`, and optional arch overrides from `asm/hash.h`. Risks include using too many bits, host word-size differences, and assuming `hash32_ptr()` is a real hash when it is only a fold. Test signals include kernel `test_hash` parity, 32-bit and 64-bit host builds, arch override comparisons, and bucket-distribution checks for table users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/hash.h -->
