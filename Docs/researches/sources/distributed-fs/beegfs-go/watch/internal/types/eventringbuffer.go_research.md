# sources/distributed-fs/beegfs-go/watch/internal/types/eventringbuffer.go

## Purpose

This file implements a simple single-cursor ring buffer for BeeWatch events. It stores pointers to protobuf events, overwrites the oldest event when full, and supports pop/peek/remove operations.

## Important APIs, Types, And Functions

`EventRingBuffer` has `buffer`, `start`, `end`, and an RW mutex. `NewEventRingBuffer` creates a size+1 buffer to distinguish full from empty. `Push` inserts and advances `end`, moving `start` on overwrite. `Pop` removes and nils the oldest event. `RemoveUntil` drops events through a sequence ID. `Peek` returns the oldest event without moving. `IsEmpty` reports `start == end`.

## Control Flow

Every mutating method locks the buffer. Push writes at `end`, advances modulo length, and if it collides with `start`, advances `start`. Pop and remove clear slots to allow garbage collection.

## State And Persistence

State is in-memory only. This buffer has one logical reader and no acknowledgement tracking, so production multi-subscriber delivery uses `MultiCursorRingBuffer` instead.

## Dependencies And Integration Points

It depends on generated `beewatch.Event` types. Tests cover it directly, but active metadata/subscriber code uses the multi-cursor buffer.

## Risks And Test Signals

`Peek` calls `IsEmpty` while holding `RLock`; Go `sync.RWMutex` permits multiple read locks by the same goroutine, so this is fine but redundant. The overwrite policy silently discards old events. Tests validate capacity, overflow ordering, pop, peek, and remove-until behavior.
