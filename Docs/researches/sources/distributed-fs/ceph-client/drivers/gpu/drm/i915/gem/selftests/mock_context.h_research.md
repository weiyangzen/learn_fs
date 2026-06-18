# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/mock_context.h

## Purpose
Declares context construction and destruction helpers used by i915 GEM selftests.

## APIs And Control Flow
Declares `mock_init_contexts()`, `mock_context()`, `mock_context_close()`, `live_context()`, `kernel_context()`, and `kernel_context_close()`. It has no executable flow beyond exposing these interfaces.

## State, Dependencies, Integration, Risks, And Tests
The header stores no state and uses forward declarations for light inclusion. It is used by huge-page, dma-buf, context, client BLT, and other tests. Risks are signature drift and callers confusing mock/live/kernel context lifetime rules. Compilation and runtime users provide validation.
