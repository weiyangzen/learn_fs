# sources/distributed-fs/coda/coda-src/dir/dirbody.c

## Purpose
Core Coda directory body implementation. It manages the 2 KB page format, blob allocation, hash chains, name/FID lookup, create/delete, directory initialization, structural validation, printing, comparison, and conversion to Venus BSD-style directory files.

## APIs, Types, and Functions
Exports `DIR_Init()`, `DIR_rvm()`, `DIR_Length()`, `DIR_Page()`, `DIR_Create()`, `DIR_Delete()`, `DIR_MakeDir()`, `DIR_Setpages()`, `DIR_Free()`, `DIR_Print()`, `DIR_PrintChain()`, `DIR_Lookup()`, `DIR_LookupByFid()`, `DIR_EnumerateDir()`, `DIR_Compare()`, `DIR_IsEmpty()`, `DIR_Hash()`, `DIR_DirOK()`, and `DIR_Convert()`. Important internals are `dir_NameBlobs()`, `dir_FindBlobs()`, `dir_AddPage()`, `dir_New()`, `dir_Extend()`, `dir_FreeBlobs()`, `dir_FindItem()`, network-order FID helpers, and `dir_DirEntry2VDirent()`.

## Control Flow, State, and Persistence
`DIR_Init()` selects RVM or VM allocation globally. Directories store a page header, allocation map, and 128 hash buckets; entries are fixed 32-byte blobs, with long names consuming contiguous blobs. Creation validates name length, rejects duplicates, allocates blobs, writes a network-order FID, and threads the entry into a hash chain. Deletion unlinks from the hash chain and frees blobs. `DIR_MakeDir()` creates one page, reserves header blobs, marks unused pages as fully free, and inserts `.` and `..`. `DIR_Convert()` rewrites entries into a Unix/Venus dirent file with block-boundary padding. `DIR_DirOK()` reconstructs expected allocation maps and verifies magic, page counts, hash bucket placement, flags, and name lengths.

## Dependencies and Integration
Depends on RVM transaction helpers, Coda kernel dirent/FID structures, LWP lock headers, and `codadir.h`/`dirbody.h`. `codadir.c` supplies locking around these routines, and `dirinode.c` persists the page data.

## Risks and Test Signals
Risks include global `dir_data_in_rvm`, transaction aborts outside RVM transactions, maximum 128 pages, fixed hash table and blob layout, case-insensitive lookup lacking correct index/preventry support, possible endian bug in page magic check for non-first pages, assertion-heavy error paths, and mmap/file truncation assumptions in conversion. Test signals are `DIR_DirOK()` after every mutation, long-name blob allocation/freeing, hash-chain lookup/delete, page growth to limits, RVM transaction enforcement, and `dirtest` conversion/listing checks.
