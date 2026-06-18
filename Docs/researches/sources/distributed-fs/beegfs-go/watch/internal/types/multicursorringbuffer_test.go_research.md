# sources/distributed-fs/beegfs-go/watch/internal/types/multicursorringbuffer_test.go

## Purpose

This file tests `MultiCursorRingBuffer` behavior across acknowledgement completion, overflow, garbage collection, cursor reset, acknowledgement edge cases, and ring-aware sequence search.

## Important APIs, Types, And Functions

`MCRBTestCase` packages named buffer fixtures. Tests include `TestAllEventsAcknowledged`, `TestPush`, `TestCollectGarbage`, `TestGetOldestAckCursor`, `TestMCRBGetEventAndResetSendCursor`, `TestAckEvent`, and `TestSearchIndexOfSeqID`.

## Control Flow

The tests use hand-built ring states for internal helpers and constructed buffers for public flows. They push sequential or intentionally skipped sequence IDs, add cursors, get events, acknowledge events, reset send cursors, and assert internal buffer/cursor positions.

## State And Persistence

The tests validate in-memory cursor and slot state directly, including nil-cleared slots after GC. This direct internal inspection gives strong regression detection for ring index math.

## Dependencies And Integration Points

It depends on generated `beewatch.Event` and testify. The tested behavior is directly consumed by metadata ingestion and subscriber handlers.

## Risks And Test Signals

Coverage is broad for deterministic index math and skipped sequence IDs, including wraparound binary search. Missing signals include concurrent race tests, `RemoveCursor`/`AddCursor` idempotence assertions, `ackError` shutdown behavior, and the exact dropped sequence ID returned by `Push`/`collectGarbage`. Adding those would catch subtle delivery-loss reporting bugs.
