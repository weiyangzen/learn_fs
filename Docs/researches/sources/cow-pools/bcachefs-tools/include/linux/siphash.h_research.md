# File Research: sources/cow-pools/bcachefs-tools/include/linux/siphash.h

Declares SipHash2-4 and HalfSipHash helpers. It defines key types, zero-key test, aligned/unaligned entry points, fixed-width integer shortcuts, and inline dispatch that chooses optimized fixed-size paths when length is compile-time constant.

The implementation in `linux/siphash.c` supplies both secure 64-bit SipHash and faster 32-bit HalfSipHash variants for hash table use.
