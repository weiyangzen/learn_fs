# sources/distributed-fs/beegfs-go/watch/internal/types/eventqueue.go

## Purpose

This file defines an older mutex-protected FIFO queue for BeeWatch events. A TODO states it is not currently used and was retained from early performance comparisons against ring-buffer designs.

## Important APIs, Types, And Functions

`EventQueue` holds a slice of `*pb.Event` and a mutex. `NewEventQueue` initializes the slice. `Push` appends an event. `Pop` returns and removes the first event or nil. `RemoveUntil` drops all events with `SeqId <= id`.

## Control Flow

All operations lock the queue mutex around slice mutation. `Pop` and `RemoveUntil` repeatedly reslice from the front, producing straightforward FIFO behavior.

## State And Persistence

State is in-memory only. No persistence or subscriber cursor support exists, which is why this structure is not the active BeeWatch event buffer.

## Dependencies And Integration Points

It depends only on generated `beewatch.Event` types. It has no current production integration points according to the file comment.

## Risks And Test Signals

`NewEventQueue(length)` creates a slice with length `length`, not capacity `length`, so a new queue initially contains `length` nil entries. If reused, that would cause early `Pop` calls to return nil before pushed events. Front-reslicing can retain underlying references and has O(n) memory movement implications over time. The file has no tests and should either be removed or fixed before use.
