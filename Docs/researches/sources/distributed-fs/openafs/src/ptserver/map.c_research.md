# sources/distributed-fs/openafs/src/ptserver/map.c

## Purpose
Implements in-memory sparse bitmap maps for supergroup support. Maps can represent positive sets or complemented sets by stealing the low bit of the map pointer as a negation flag.

## Important APIs, Types, And Functions
When `SUPERGROUPS` is enabled, exports `in_map`, `free_map`, `add_map`, `and_map`, `or_map`, `not_map`, `copy_map`, `count_map`, `next_map`, `first_map`, `prev_map`, `last_map`, `negative_map`, `bic_map`, and optional `print_map`, `read_map`, `write_map`. Internal `struct bitmap` stores a linked list of pages, each with `MDATA` integer bit words. Macros map node numbers to page/index/bit and toggle negation.

## Control Flow
Membership checks locate the node's page and return the stored bit XOR complement flag. Adding allocates a page when needed, initializes it to all zeroes or all ones depending on map polarity, then sets or clears the bit. Boolean operations destructively combine bitmap page lists, freeing consumed right-hand pages. Iterators scan pages/words/bits to find next or previous set nodes and reject negative maps.

## State And Persistence
State is heap-allocated bitmap linked lists. Many operations consume/free input map pages, so ownership is part of the API contract. No disk state is written.

## Dependencies And Integration Points
Used by protection-server supergroup logic through `map.h`. Depends on OpenAFS debug globals only for optional diagnostics.

## Risks And Test Signals
Risks include pointer-tagging portability, destructive boolean operation ownership surprises, negative map count returning one's complement, allocation failure handling bug that calls `free_map` on the newly failed pointer path, and lack of code when `SUPERGROUPS` is disabled. Test signals are set algebra identities, iteration order, complement behavior, large sparse IDs, and memory leak/error-path checks.
