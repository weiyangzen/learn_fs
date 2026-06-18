# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ipack.h

## Purpose
This small header exposes the AV7110 PES repacker lifecycle and input functions. It intentionally does not define `struct ipack`; callers include `dvb_filter.h` for the parser state structure and stream constants.

## Important APIs
The public functions are `av7110_ipack_init()`, `av7110_ipack_reset()`, `av7110_ipack_instant_repack()`, `av7110_ipack_free()`, and `av7110_ipack_flush()`. The init callback signature is `void (*func)(u8 *buf, int size, void *priv)`, matching the emitter used by `send_ipack()`.

## Control Flow and State
The header defines no control flow by itself. The lifecycle implied by the API is initialize once, feed byte chunks repeatedly, optionally flush an open indefinite-length packet, reset when needed, and free the allocated buffer.

## Dependencies and Integration Points
It requires a visible `struct ipack` and `u8` type from included kernel/media headers, normally through `dvb_filter.h`. It is used by AV7110 code that needs incremental PES parsing and callback emission.

## Risks and Test Signals
The main API risk is include-order fragility because `struct ipack` is not declared here. Tests should compile all call sites, verify init/free pairing, and exercise reset/flush behavior through `av7110_ipack.c`.
