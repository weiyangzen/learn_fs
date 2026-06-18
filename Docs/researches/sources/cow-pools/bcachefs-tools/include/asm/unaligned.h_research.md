# File Research: sources/cow-pools/bcachefs-tools/include/asm/unaligned.h

Purpose: selects endian-correct unaligned access helpers for the userspace kernel-shim environment.

Key contents:
- On little endian, includes little-endian struct helpers and big-endian byteshift helpers, then maps `get_unaligned`/`put_unaligned` to little-endian variants.
- On big endian, does the inverse.
- Fails compilation if endianess is not known.

Important interactions:
- Used by crypto and on-disk format code that expects kernel unaligned helpers.
