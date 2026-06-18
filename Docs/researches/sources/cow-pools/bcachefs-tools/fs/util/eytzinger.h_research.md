# File Research: sources/cow-pools/bcachefs-tools/fs/util/eytzinger.h

Header for Eytzinger array layout helpers. It documents why the layout improves branch prediction/cache behavior compared with binary search and provides child, first/last, next/prev, inorder conversion, and traversal macros for one-based and zero-based indexing.

Inline search helpers return exact matches or lower/upper bounds, with one-based functions returning 0 for not found and zero-based functions returning -1. Sort function prototypes cover comparator-only and comparator-with-private-data variants.
