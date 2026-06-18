# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/eytzinger.c

This file implements sorting into Eytzinger array layout, with generic compare/swap support and optimized swap routines.

Major components:
- Alignment detection for choosing word-sized swap paths.
- Swap implementations:
  - 64-bit word swaps
  - 32-bit word swaps
  - byte swaps
  - caller-provided wrapper swap
- Compare wrapper support for both `cmp_func_t` and `cmp_r_func_t`.
- `eytzinger1_sort_r()`:
  - converts array into one-based Eytzinger layout using heap-sort-like operations
  - supports private compare context
  - picks optimized swap mode when no swap function is supplied
  - calls `cond_resched()` during long operations
- `eytzinger1_sort()` wraps non-private compare/swap functions.
- `eytzinger0_sort_r()` and `eytzinger0_sort()` adapt zero-based arrays by shifting base pointer.

Important invariants:
- One-based layout assumes the caller has reserved index 0.
- Sorting uses `inorder_to_eytzinger1()` to map logical sorted positions to tree-layout positions.
- The code is generic over element size and comparison function.

Research notes:
- Snapshot deletion uses one-based Eytzinger darray helpers for fast membership checks.
- This implementation is performance-focused and mirrors kernel sort-style callback conventions.
