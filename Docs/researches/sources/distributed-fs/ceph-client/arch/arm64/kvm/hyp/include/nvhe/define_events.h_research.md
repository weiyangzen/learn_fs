# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/define_events.h

## Purpose

This header materializes hyp event ID objects for each event declared in `asm/kvm_hypevents.h`.

## Important APIs, Types, And Functions

It redefines `HYP_EVENT()` to emit `struct hyp_event_id hyp_event_id_<name>` in a dedicated `.hyp.event_ids.<name>` section with `.enabled = ATOMIC_INIT(0)`.

## Control Flow

There is no runtime flow in the header itself. Inclusion expands the event list and creates linker-visible event descriptors.

## State And Persistence Behavior

Each event gets persistent hyp data containing at least an enabled atomic and later assigned IDs.

## Dependencies And Integration Points

It feeds `events.c` and nVHE tracing. The linker exposes `__hyp_event_ids_start/end`.

## Risks And Test Signals

Risks are section naming/linker ordering mismatches and event-list macro drift. Test signals are valid event ID ranges and successful enable/disable by event index.
