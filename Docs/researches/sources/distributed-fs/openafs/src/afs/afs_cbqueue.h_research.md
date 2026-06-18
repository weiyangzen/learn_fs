# sources/distributed-fs/openafs/src/afs/afs_cbqueue.h

Purpose: Defines the callback-expiration wheel geometry and the queue-entry-to-vcache conversion macro used by `afs_cbqueue.c`.

Important APIs and definitions: `CBHTSLOTLEN` is 128 seconds, `CBHTSIZE` is 128 slots, `CBHash(t)` shifts seconds into slots, and `CBQTOV(e)` computes the containing `struct vcache` from its embedded `callsort` queue entry.

Control flow: No runtime logic exists here; the macros shape the bucket selection and object recovery behavior in queue operations.

State and persistence: No state or persistence. The values define the granularity and range of volatile callback queue state.

Dependencies and integration points: Requires `struct vcache` to contain a `callsort` field matching the pointer arithmetic in `CBQTOV`. Included by callback queue management.

Risks: `CBQTOV` is manual container-of pointer arithmetic and will break if `struct vcache` layout or `callsort` type changes without updating the macro. The slot length is encoded as a shift in `CBHash`, so changing `CBHTSLOTLEN` requires updating the shift assumption.

Test signals: Compile/layout tests for `CBQTOV`, bucket mapping around 127/128/129 seconds, and queue behavior after any callback-wheel constant changes.
