
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.h

## Purpose

`xe_pagefault.h` declares the consumer page-fault lifecycle API for device initialization, GT reset, and producer fault submission.

## Important APIs, Types, and Functions

It exposes `xe_pagefault_init()`, `xe_pagefault_reset()`, and `xe_pagefault_handler()`.

## Control Flow

Probe initializes queues after fuse/topology data is available. Producers submit parsed faults through `xe_pagefault_handler()`. Reset code calls `xe_pagefault_reset()` to squash queued faults for a resetting GT.

## State and Persistence Behavior

State is stored in `xe_device.usm` fields defined elsewhere and in `xe_pagefault_types.h`.

## Dependencies and Integration Points

It forward declares `xe_device`, `xe_gt`, and `xe_pagefault` for use by fault producers and reset paths.

## Risks and Edge Cases

Callers must not submit faults before initialization on USM devices. Reset callers should invoke the reset function before stale GT work can be acknowledged as live.

## Test Signals

Build coverage and producer integration tests should validate init/handler/reset call sequencing.
