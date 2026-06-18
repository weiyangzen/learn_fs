# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-controls.h

## Purpose
This header exposes the cx18-specific `cx2341x_handler_ops` table to driver initialization code.

## Important APIs, Types, and Functions
The only declared symbol is `extern const struct cx2341x_handler_ops cx18_cxhdl_ops;`. It is consumed by `cx18-driver.c` when initializing `cx->cxhdl`.

## Control Flow
No runtime flow exists in the header. It links the control callback implementation in `cx18-controls.c` into the main device initialization path.

## State and Persistence
The ops table is static read-only code/data. Runtime state affected by those callbacks lives in `struct cx18`, `struct cx2341x_handler`, VBI buffers, and subdevices.

## Dependencies and Integration Points
This is a narrow integration point between the main driver and cx2341x MPEG controls. It assumes including files already know `struct cx2341x_handler_ops`.

## Risks and Edge Cases
Because the header has no include guard and no includes, it relies on include order through `cx18-driver.h` or other media headers. Moving it into a different compilation context could require forward declarations or includes.

## Test Signals
Build coverage is the primary signal: `cx18-driver.c` must resolve `cx18_cxhdl_ops`, and MPEG control changes should invoke the callbacks documented in `cx18-controls.c`.
