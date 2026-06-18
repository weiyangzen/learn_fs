# sources/distributed-fs/ceph-client/scripts/dtc/data.c

## Purpose
`data.c` implements DTC's growable binary data buffers and marker lists used for property values, references, labels, typed arrays, strings, reserves, and inserted fixups.

## Important APIs, Types, and Functions
Public functions include `data_free()`, `data_grow_for()`, `data_copy_mem()`, `data_copy_escape_string()`, `data_copy_file()`, `data_append_data()`, `data_insert_at_marker()`, `data_merge()`, integer append helpers, `data_add_marker()`, `data_is_one_string()`, `data_insert_data()`, and `alloc_marker()`. It uses `struct data` and `struct marker` from `dtc.h`.

## Control Flow and State
Data buffers are immutable-by-value at the API surface but contain owned heap pointers. Append and insert operations return updated structs after reallocating and adjusting markers. `data_merge()` appends `d2` bytes to `d1`, splices `d2` markers into `d1`, offsets them by `d1.len`, clears `d2.markers`, and frees `d2.val`. `data_copy_file()` grows in chunks until EOF or max length.

## Dependencies and Integration
It depends on `xmalloc`, `xrealloc`, `xstrdup`, `die`, `get_escape_char`, and libfdt endian conversion helpers. Parser, tree source, flattree, and checks code all depend on these buffers.

## Risks and Test Signals
Ownership transfer in `data_merge()` and marker copying in `data_insert_data()` are subtle. `data_grow_for()` doubles from `xlen` and assumes arithmetic does not overflow except where explicitly checked in file reads. Test append/merge marker offsets, escaped strings, max-length file reads, integer endian output, alignment, insertion at markers, and free-after-merge behavior.
