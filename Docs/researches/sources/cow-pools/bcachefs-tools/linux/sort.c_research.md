# File Research: sources/cow-pools/bcachefs-tools/linux/sort.c

## Purpose
Kernel-style non-recursive heapsort implementation.

## Key Responsibilities
- Implements `sort_r()` with optional private data passed to comparator/swapper.
- Chooses optimized default swap routines for 64-bit words, 32-bit words, or bytes.
- Supports wrapper compatibility for traditional `sort()`-style comparator/swap signatures.

## Algorithm
- Bottom-up heapsort.
- O(n log n) average and worst-case behavior.
- Reduces comparator calls by finding the sift-down path to leaves before backtracking.

## Important Details
- `is_aligned()` chooses word-wide swapping only when element size and base alignment permit it.
- `parent()` computes byte-offset parents without full division at each step.
- Built-in swapping avoids slower indirect calls when possible.

## Dependencies
Uses `linux/sort.h`, compiler/type/export helpers.
