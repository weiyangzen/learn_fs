# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lrc_types.h

## Purpose
`xe_lrc_types.h` defines the core `struct xe_lrc` storage used by logical ring contexts.

## Important APIs, Types, And Functions
- `struct xe_lrc` stores the context/ring BO, seqno BO, size, replay size, owning GT, flags, refcount, ring state, descriptor, hardware fence context, and cached timestamp.
- Flags indicate indirect context and indirect ring-state page usage.
- Forward-declares `struct xe_lrc_snapshot`.

## Control Flow
The implementation allocates and initializes this structure in `xe_lrc_create()`, while users interact through the public API and refcount helpers.

## State And Persistence
This is persistent per-context state. The ring tail is driver-owned shadow state; seqno memory is GPU-written and CPU-read; descriptor and flags define GPU execution context identity and layout.

## Dependencies And Integration Points
Depends on Linux kref and Xe hardware fence types. It is used by scheduler, execution queues, fencing, and debug/recovery paths.

## Risks
The structure binds memory objects and fence context lifetime. Any direct mutation outside LRC helpers risks desynchronizing software tail, descriptor bits, or timestamp state from hardware-visible memory.

## Test Signals
Lifetime/refcount tests and creation/destruction tests should verify BOs, fence context, and cached fields are initialized and released in the right order.
