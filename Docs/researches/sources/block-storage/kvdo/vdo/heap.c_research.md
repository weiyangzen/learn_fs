# File Research: sources/block-storage/kvdo/vdo/heap.c

## Purpose
Implements a generic in-place max-heap wrapper over caller-owned arrays, including heapify, pop-max, full sort, and incremental sort.

## Main Behavior
- `initialize_heap()` stores comparator/swapper/capacity/element size and shifts the array pointer so indexes can be treated as 1-based byte offsets.
- `build_heap()` heapifies up to capacity using bottom-up sift-down in O(N).
- `pop_max_heap_element()` removes the root, optionally copies it to the caller, moves the final leaf to root, and restores heap invariant.
- `sort_heap()` performs in-place heapsort, leaving the heap empty and array sorted from minimum to maximum.
- `sort_next_heap_element()` performs one heapsort step and returns the next sorted element pointer.

## Dependencies
Uses caller-provided comparator and swapper, numeric min helper, status/error headers, and standard memory copy.

## Notable Risk
`sift_heap_down()` computes `right_child` as `left_child + heap->element_size`; this is consistent with the file’s byte-offset indexing scheme, but any future change to element-index rather than byte-index arithmetic would break the heap.
