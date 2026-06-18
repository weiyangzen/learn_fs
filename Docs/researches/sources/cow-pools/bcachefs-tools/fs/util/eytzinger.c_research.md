# File Research: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.c

Implements Eytzinger-layout sorting for one-based and zero-based arrays. It includes optimized swap helpers for aligned 64-bit, aligned 32-bit, and byte-wise copying, plus wrapper support for comparator/swap signatures.

`eytzinger1_sort_r()` heapifies and sorts using Eytzinger index conversion so final array order supports cache-friendly Eytzinger search/traversal. Zero-based sort is implemented by biasing the base pointer and reusing the one-based routine. Contains disabled benchmark/test code.
