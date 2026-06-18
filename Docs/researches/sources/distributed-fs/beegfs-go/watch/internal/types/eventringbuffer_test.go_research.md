# sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer_test.go

## Purpose

This file tests the simple `EventRingBuffer` implementation for initialization, overflow ordering, pop/peek semantics, and sequence-based removal.

## Important APIs, Types, And Functions

`TestNewEventBuffer` checks that internal capacity is requested size plus one. `TestEventBufferPushPop` pushes many events through a small buffer and verifies only the most recent capacity-sized window remains. `TestRemoveUntil` pushes events, removes through sequence ID 5, and confirms the remaining count.

## Control Flow

Tests create generated `pb.Event` values with sequential `SeqId`, push them into the buffer, then pop/peek and assert expected sequence IDs and empty states.

## State And Persistence

All state is in-memory. Tests intentionally cause overflow to validate destructive retention behavior.

## Dependencies And Integration Points

It depends on testify and generated `beewatch.Event`. The tested buffer is not the active multi-subscriber buffer, but it documents the simpler ring-buffer semantics used as a baseline.

## Risks And Test Signals

`TestRemoveUntil` comment says five items remain after removing through 5 from events 0..10, and the loop indeed expects five pops for IDs 6..10. Missing cases include wraparound removal, remove on empty buffer, and concurrent access.
