<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist_hashes.c -->
# sources/distributed-fs/ceph-client/certs/blacklist_hashes.c

## Purpose

`blacklist_hashes.c` defines the compiled-in blacklist hash array by including the generated `blacklist_hash_list` file.

## Important APIs, Types, And Functions

The sole symbol is `const char __initconst *const blacklist_hashes[]`. There are no functions. It includes `blacklist.h` and then includes the generated list inside the array initializer.

## Control Flow

Control flow occurs in `blacklist.c`, which iterates this array until `NULL`. This file only contributes data.

## State And Persistence Behavior

The data is `__initconst`, used during boot initialization and discardable afterward. The persistent source is the configured `CONFIG_SYSTEM_BLACKLIST_HASH_LIST` input in the build environment.

## Dependencies And Integration Points

It depends on the generated `blacklist_hash_list` header-like file produced by `certs/Makefile`. The Makefile adds `-I $(obj)` so the generated include is found from the object directory.

## Risks And Edge Cases

If `blacklist_hash_list` lacks a terminating `NULL` or contains invalid C strings, this file can break compilation or boot. The Makefile generates `NULL` for an empty config and validates populated lists with the AWK checker.

## Test Signals

Build with empty and populated hash list configurations. Inspect the preprocessed initializer or boot behavior to ensure all entries are loaded and duplicate entries are reported without fatal failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist_hashes.c -->
