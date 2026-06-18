# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/ipu3-css-pool.h

## Purpose
`ipu3-css-pool.h` defines the CSS DMA map descriptor and fixed-size parameter pool shared by CSS, DMA, and parameter code.

## Important APIs, Types, and Functions
- `IPU3_CSS_POOL_SIZE` is four.
- `struct imgu_css_map` records size, CPU virtual address, device IOVA, and backing pages.
- `struct imgu_css_pool` stores four maps with validity flags plus a newest-entry pointer.
- Function declarations cover resize, init, cleanup, get, put, and last lookup.

## Control Flow
CSS initializes maps and pools during setup, advances pools during parameter submission, and cleans them during pipeline teardown.

## State and Persistence Behavior
`imgu_css_map` binds CPU memory to firmware-visible IOVA. `imgu_css_pool` persists recent generations for safe firmware consumption and old-value reuse.

## Dependencies and Integration Points
The header is included by CSS state, pool implementation, and DMA mapping code. It is the shared memory ownership contract.

## Risks
Raw address ownership is implicit. Mispaired cleanup or stale map use can leak memory or expose invalid IOVAs to firmware.

## Test Signals
Verify all pool users agree on ownership and that every allocated map is freed exactly once during CSS cleanup.
