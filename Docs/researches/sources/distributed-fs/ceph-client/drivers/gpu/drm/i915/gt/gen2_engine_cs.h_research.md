# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen2_engine_cs.h

## Purpose
Declares gen2/gen4/gen5 engine command-streamer operations for flushes, breadcrumbs, batch starts, and IRQ control.

## APIs And Control Flow
Declares the flush, breadcrumb, batch-start, and IRQ functions implemented in `gen2_engine_cs.c`. The header has no executable flow.

## State, Dependencies, Integration, Risks, And Tests
It stores no state and depends on Linux integer types plus forward declarations for request and engine structs. Engine setup code uses it to assign legacy platform ops. Risks are prototype drift or using the wrong generation helper for a platform. Build coverage and legacy request-submission tests validate it.
