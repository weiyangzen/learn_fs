<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h

## Purpose
Declares a minimal TI K3 event-router callback structure for routing DMA events.

## Important APIs, Types, And Functions
`struct k3_event_route_data` stores private data and a `set_event()` callback that programs a selected event.

## Control Flow
A consumer receives route data and calls `set_event(priv, event)` to configure event routing for a DMA or peripheral path.

## State And Persistence
State is provider private data and hardware event-router programming. No persistence exists.

## Dependencies And Integration Points
Depends only on kernel integer types and integrates TI K3 DMA/peripheral glue with event-router providers.

## Risks And Edge Cases
The callback must validate event IDs and provider lifetime. Consumers must not call after the provider is removed.

## Test Signals
Tests should cover valid/invalid event selection, provider removal, multiple consumers, and event delivery after routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/k3-event-router.h -->
