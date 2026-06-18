# File Research: sources/cow-pools/bcachefs-tools/linux/generic-radix-tree.c

Implements generic radix tree allocation, lookup, iteration, preallocation, and freeing. Tree roots encode depth in low bits; allocation grows root depth with cmpxchg and zeroed nodes. Iterators skip missing subtrees forward or backward.

Concurrency relies on atomic root/child publication and caller-side lifetime discipline.
