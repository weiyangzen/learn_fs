# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_pagefault.h

## Purpose
Declares the GuC page-fault G2H handler.

## Important APIs, Types, And Functions
Forward-declares `struct xe_guc` and declares `xe_guc_pagefault_handler(struct xe_guc *guc, u32 *msg, u32 len)`.

## Control Flow
GuC CT message dispatchers call this handler when a page-fault message arrives.

## State And Persistence
The header owns no state. Handler state is transient in the implementation.

## Dependencies And Integration Points
Includes Linux integer types and is consumed by GuC CT receive dispatch code.

## Risks And Test Signals
The interface exposes raw message dwords and length, so callers must pass the exact GuC payload. Compile coverage and CT dispatch tests validate it.
