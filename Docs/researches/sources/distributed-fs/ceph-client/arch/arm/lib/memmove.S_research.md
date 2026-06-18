# sources/distributed-fs/ceph-client/arch/arm/lib/memmove.S

Purpose: implements `__memmove` and weak `memmove`, supporting overlapping memory ranges.

Control flow compares destination/source distance; non-overlapping or safe forward cases branch to `__memcpy`, while overlapping destructive cases copy backward from the end with alignment, unrolled 32-byte loops, source-shift paths, and byte tails. State is only destination memory and registers. Dependencies include assembler endian byte-lane macros, PLD/CALGN options, and `__memcpy`. Risks are off-by-one overlap detection, backward unaligned source reconstruction, and return-value preservation. Test signals include memmove overlap matrices, all alignments, and small tail sizes.
