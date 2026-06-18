# sources/distributed-fs/ceph-client/fs/dlm/util.h

## Purpose
`util.h` declares DLM errno conversion helpers.

## Important APIs, Types, And Functions
It exposes `to_dlm_errno()` and `from_dlm_errno()`.

## Control Flow
Callers convert before sending result codes on the wire and convert back after receiving them.

## State And Persistence
No state. The implementation's constants are part of DLM protocol compatibility.

## Dependencies And Integration Points
Included by lock, requestqueue, rcom, and other files that log or transmit DLM result codes.

## Risks
Forgetting to convert a wire-visible error can create architecture-dependent behavior in mixed clusters.

## Test Signals
Build coverage and cross-architecture protocol tests should validate the mapping remains consistent.
