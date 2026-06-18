# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctimap.c

## Purpose

This file implements generic circular input-mapper list management used to program hardware mapper RAM for resources such as SRCIMP.

## Important APIs, types, and functions

`input_mapper_add()` inserts an `imapper` ordered by input slot and updates the new entry plus the predecessor through a caller-supplied `map_op`. `input_mapper_delete()` removes an entry, rewires the predecessor to the next entry, and clears the single-node case. `free_input_mapper_list()` deletes and frees every mapper node on a list.

## Control flow

Add handles the empty list by making the entry point to itself, otherwise scans by slot, inserts before the first larger slot or at the tail, computes predecessor and successor with wraparound, then invokes `map_op` for changed entries. Delete computes wraparound predecessor and successor; a one-node list is zeroed and unmapped, while multi-node removal updates the predecessor before deleting the target.

## State and persistence behavior

State is the caller-owned `struct list_head` plus each `struct imapper`'s `slot`, `user`, `addr`, and `next`. Hardware persistence is delegated to `map_op`, so list changes and hardware programming stay paired.

## Dependencies and integration points

It depends on Linux list primitives and `ctimap.h`. `ctsrc.c` uses it in `srcimp_imap_add()` and `srcimp_imap_delete()` while holding `imap_lock`, with `srcimp_map_op()` programming SRC input mapper registers.

## Risks and test signals

Risks include unordered duplicates, deleting an entry not on the list, map operation failures being ignored, and wraparound mistakes corrupting the hardware chain. Useful tests allocate multiple mapper entries with sorted, tail, head, and single-entry deletion cases and verify callback order plus final `next` links.
