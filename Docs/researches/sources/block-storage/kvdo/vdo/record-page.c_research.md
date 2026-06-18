# File Research: sources/block-storage/kvdo/vdo/record-page.c

Read completely: 113 lines.

This file encodes and searches UDS record pages. `encode_record_page()` builds an array of pointers to chapter records, sorts the pointers by chunk name using the volume's radix sorter, and copies records into the output page in heap-ordered binary search tree layout. `encode_tree()` performs the in-order traversal that converts the sorted array into tree order.

`search_record_page()` treats a record page as an array of `struct uds_chunk_record`, compares the requested chunk name against records starting at heap index 0, and walks left or right with child indexes `2N + 1` and `2N + 2`. When found, it optionally copies the record metadata to the caller.

Dependencies: `volume->geometry`, `volume->record_pointers`, `volume->radix_sorter`, `radix_sort()`, UDS chunk record/name/data definitions, `memcmp`, `memcpy`, and static assertions on record layout.

Security/reliability notes: encoding assumes `volume->record_pointers` is sized for `records_per_page` and that chunk name is at offset 0 in `struct uds_chunk_record`. Search trusts geometry/page consistency.
