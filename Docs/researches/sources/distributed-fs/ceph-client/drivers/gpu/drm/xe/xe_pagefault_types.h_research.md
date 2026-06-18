
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault_types.h

## Purpose

`xe_pagefault_types.h` defines the producer-consumer page fault ABI inside the Xe driver: access/type enums, acknowledgement ops, compact fault record, and queue structure.

## Important APIs, Types, and Functions

- `enum xe_pagefault_access_type`: read, write, and atomic access encodings.
- `enum xe_pagefault_type`: not-present, write access violation, and atomic access violation.
- `struct xe_pagefault_ops`: producer callback `ack_fault()`.
- `struct xe_pagefault`: 64-byte record with GT pointer, consumer fields, producer-private state, producer ops, and original message words.
- `struct xe_pagefault_queue`: byte-oriented circular queue with data pointer, size, head/tail, spinlock, and worker.
- Bit masks: access type mask, prefetch bit, NACK sentinel, fault level/type masks, and producer message length.

## Control Flow

Fault producers fill `struct xe_pagefault`, including producer-private acknowledgement data, then pass it to the consumer queue. The consumer reads only consumer fields plus producer ops for acknowledgement and leaves producer-private payload interpretation to the producer.

## State and Persistence Behavior

Fault records are copied into queues and are transient until worker acknowledgement. Queue state persists for USM lifetime. Producer message words are retained because fault producers may run in allocation-constrained contexts.

## Dependencies and Integration Points

The types are embedded in `xe_device` USM state and included by hardware/firmware fault producers and the consumer implementation.

## Risks and Edge Cases

- The compact layout relies on small integer fields and masks; producers must pack values correctly.
- `XE_PAGEFAULT_TYPE_LEVEL_NACK` lets producers force a negative acknowledgement before service.
- Queue head/tail are byte offsets, and entry size is rounded to a power of two in implementation.

## Test Signals

Tests should validate struct size expectations, mask packing/unpacking, NACK behavior, prefetch flag behavior, queue wraparound, and producer callback invocation with preserved message words.
