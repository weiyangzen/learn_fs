# sources/distributed-fs/ceph-client/arch/arm/lib/findbit.S

Purpose: implements little-endian and, on big-endian builds, big-endian find-first/find-next set and zero bit helpers. Entry points include `_find_first_zero_bit_le`, `_find_next_zero_bit_le`, `_find_first_bit_le`, `_find_next_bit_le`, and BE variants.

Control flow scans words until a candidate nonzero word is found, adjusts for start offset in next-bit calls, reverses bytes where endian semantics require, then uses `rbit/clz`, `clz` tricks, or manual bit tests depending on CPU generation. State is none beyond input bitmap reads. Dependencies include endian macros and bitops API naming. Risks are off-by-one exclusive size handling, endian bit order confusion, and CPU instruction availability. Test signals include bitmap selftests over all sizes, offsets, zero-size calls, and BE/LE configurations.
