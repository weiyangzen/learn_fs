# File Research: sources/cow-pools/bcachefs-tools/c_src/ida.c

- Userspace replacement for kernel IDA allocation.
- Implements a flat eytzinger-layout d-ary bitmap tree where set bits mean free IDs.
- Supports growth by adding a tree level and moving the old tree into the leftmost subtree.
- Provides initialization, destruction, range allocation, batch allocation, free, and first-allocated lookup.
- Uses a mutex for synchronization and optional debug invariant verification.
- Carefully bounds shifts/capacity to avoid undefined behavior and overflow.
