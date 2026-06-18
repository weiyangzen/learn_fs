# File Research: sources/block-storage/lvm2/lib/datastruct/str_list.h

## Purpose
Declares LVM2 string-list helpers layered on `dm_list` and `dm_pool`.

## Public Surface
The header documents return conventions, creation, add/prepend, duplicate-aware and no-duplicate-check insertion, deletion, wipe, match, list equality, duplication, join, and split helpers.

## Integration
The functions are generic utilities for LVM2 modules that need ordered lists of string pointers without introducing a separate container type.

## Risk Notes
The header explicitly notes that `str_list_dup()` initializes caller-provided list storage and that no-duplicate-check insertion requires caller-side duplicate discipline.
