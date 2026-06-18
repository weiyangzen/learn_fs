# File Research: sources/cow-pools/bcachefs-tools/fs/util/darray.c

Implements dynamic-array resizing. Growth rounds requested element count up to a power of two, checks multiplication overflow, uses `kvmalloc`/aligned kernel allocation for smaller allocations and `vmalloc` for very large allocations, copies existing entries, RCU-publishes the new data pointer, updates capacity, and frees old storage immediately or via RCU as requested.

It supports preallocated inline storage by avoiding freeing the embedded buffer.
