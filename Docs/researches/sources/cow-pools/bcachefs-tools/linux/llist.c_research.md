# File Research: sources/cow-pools/bcachefs-tools/linux/llist.c

Implements lockless singly-linked list operations: batch add with cmpxchg, delete-first for single-consumer use, and reverse-order helper. Used by closure wait lists and other lockless queue paths.
