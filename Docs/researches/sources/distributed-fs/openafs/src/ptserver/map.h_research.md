# sources/distributed-fs/openafs/src/ptserver/map.h

## Purpose
Declares the opaque map API used by protection-server supergroup code.

## Important APIs, Types, And Functions
Forward-declares `struct map` and declares membership, allocation/free, boolean set operations, copying, counting, iteration, complement inspection, subtraction, and printing functions.

## Control Flow
Callers create/update maps with `add_map`, combine them with `and_map`, `or_map`, `not_map`, and `bic_map`, query with `in_map` and `count_map`, iterate with first/next/last/prev helpers, and release with `free_map`.

## State And Persistence
The header hides representation and stores no state. Implementation state is heap-backed sparse bitmaps in `map.c`.

## Dependencies And Integration Points
Included by supergroup-aware ptserver code when `SUPERGROUPS` is enabled.

## Risks And Test Signals
Risks are hidden destructive ownership semantics not visible in declarations and no const-correctness. Test signals are compilation against `map.c` and supergroup membership tests.
