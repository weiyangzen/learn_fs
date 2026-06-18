# sources/distributed-fs/ceph-client/kernel/printk/printk_ringbuffer.c

## Purpose
`printk_ringbuffer.c` implements the lockless storage engine behind printk records. It manages two coordinated rings: a descriptor ring containing record metadata, sequence numbers, state, and logical text-block locations, and a text data ring containing ID-prefixed text payload blocks. The design lets writers reserve and commit records from any context while readers detect overwritten, missing, unfinalized, or finalized records without taking writer-side locks.

## Important APIs, types, and functions
The public writer APIs are `prb_reserve()`, `prb_reserve_in_last()`, `prb_commit()`, `prb_final_commit()`, `prb_init()`, and `prb_record_text_space()`. Public reader APIs are `prb_read_valid()`, `prb_read_valid_info()`, `prb_first_seq()`, `prb_first_valid_seq()`, `prb_next_seq()`, and `prb_next_reserve_seq()`. Internally, descriptor lifecycle is handled by `desc_reserve()`, `desc_read()`, `desc_push_tail()`, `desc_make_reusable()`, `desc_make_final()`, and `desc_update_last_finalized()`. Text storage is handled by `data_alloc()`, `data_realloc()`, `data_push_tail()`, `data_make_reusable()`, `get_data()`, `copy_data()`, and helpers for logical-position wrapping.

## Control flow
A writer initializes a `printk_record`, saves local IRQ flags, reserves a descriptor, assigns the next sequence number, finalizes the previous committed record if needed, allocates text storage, fills `r->info` and `r->text_buf`, then commits. `prb_commit()` leaves the newest record reopenable until a newer reservation or explicit finalization, while `prb_final_commit()` makes it immediately readable. `prb_reserve_in_last()` reopens the newest committed descriptor if the caller ID matches and extends or allocates its text block within a caller-supplied maximum.

Readers map sequence numbers to descriptors, validate descriptor ID and state before and after metadata/text copies, and skip lost records. `_prb_read_valid()` catches readers up to the current tail, skips records whose payload was overwritten, and has panic-CPU logic to continue past non-finalized gaps when panic printing must drain finalized data.

## State and persistence behavior
All state is in caller-provided memory: descriptor array, `printk_info` array, text buffer, atomic head/tail IDs, atomic data head/tail logical positions, `last_finalized_seq`, and reserve-failure counter. Records persist only until overwritten by ring reuse. Special logical positions represent empty-line records and failed/lost data. The bootstrap state uses the final descriptor as initial head/tail so the first real record gets sequence 0 while early readers see an empty buffer.

## Dependencies and integration points
The file depends on Linux atomics, interrupt flag management, memory barriers, KUnit visibility exports, printk internals (`panic_on_this_cpu()`, `debug_non_panic_cpus`, `legacy_allow_panic_sync`), and metadata structures from `printk_ringbuffer.h`. It is consumed by the printk core and directly stress-tested by the KUnit ringbuffer test.

## Risks and invariants
The highest-risk area is memory ordering. The implementation documents barrier pairs with `LMM(...)` labels, and regressions can expose stale descriptors, torn metadata/text reads, ABA failures on 32-bit, or unsafe reuse before readers have validated state. Descriptor tail must always point at a finalized or reusable descriptor. Data tail movement must make associated descriptors reusable before storage reuse. `text_len` must be sane relative to allocated text space for readers and extension logic. Reserve/commit windows disable local interrupts to reduce self-deadlock and full-ring stalls.

## Test signals
Strong signals are KUnit concurrent reader/writer stress, wraparound tests, empty and failed data blocks, reopen/extend cases, panic read behavior, sequence gap detection, and lockdep/KCSAN coverage around atomics and barriers. Failures usually appear as bad sequence reads, invalid text payloads, warnings from strict block validation, or reserve failures increasing under heavy contention.
