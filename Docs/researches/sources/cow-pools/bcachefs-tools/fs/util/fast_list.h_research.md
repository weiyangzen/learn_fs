# File Research: sources/cow-pools/bcachefs-tools/fs/util/fast_list.h

Public fast-list interface. Defines `struct fast_list` as a generic radix tree of pointers plus IDA and per-CPU buffer. Iteration skips NULL slots with a `genradix_iter`, and macros provide full or start-offset iteration.

Exports slot reservation/return, add/remove, direct set, init, and exit. The design supports lockless add/remove/iteration except when per-CPU slot buffers refill or drain.
