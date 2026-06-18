<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/jhash.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/jhash.h

## Purpose
`jhash.h` provides Jenkins lookup3-style 32-bit hashing for arbitrary bytes and arrays of 32-bit words.

## APIs And Flow
Important APIs are `jhash_size()`, `jhash_mask()`, `JHASH_INITVAL`, `__jhash_mix`, `__jhash_final`, `jhash()`, `jhash2()`, `__jhash_nwords()`, `jhash_3words()`, `jhash_2words()`, and `jhash_1word()`. `jhash()` consumes 12-byte blocks using unaligned 32-bit loads, handles the final tail with fall-through cases, and finalizes into `c`; `jhash2()` performs the same mixing over u32 words.

## State, Dependencies, Risks, Tests
There is no persistent state. Dependencies are `linux/bitops.h` for `rol32` and `linux/unaligned/packed_struct.h` for byte-safe loads. Risks include endian-dependent byte hashes, fall-through warning sensitivity, and using the non-cryptographic hash for adversarial inputs. Tests should compare vectors with the kernel copy, exercise lengths 0 through 12 and longer, verify word-array hashing, and run on big-endian and little-endian hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/jhash.h -->
