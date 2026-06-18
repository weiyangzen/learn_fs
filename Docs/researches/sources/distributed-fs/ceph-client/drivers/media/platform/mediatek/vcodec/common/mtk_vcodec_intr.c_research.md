# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_intr.c

## Purpose
This file implements a shared wait helper for vcodec hardware completion interrupts.

## Important APIs, Types, And Functions
`mtk_vcodec_wait_for_done_ctx()` receives a decoder or encoder context pointer, command ID, timeout in milliseconds, and hardware index. It infers instance type from the first context field, selects context ID/type, interrupt condition/type arrays, waitqueue array, and platform device, then waits for `ctx_int_cond[hw_id]` with `wait_event_interruptible_timeout()`.

## Control Flow
Codec-specific worker code enables hardware and starts decode/encode. Interrupt handlers set condition/type and wake the queue. This helper blocks until the condition is true, timeout expires, or a signal interrupts the wait. It logs timeout/interruption and clears condition/type before returning 0 or -1.

## State, Persistence, And Dependencies
It mutates per-context interrupt condition and type arrays. There is no persistence. Dependencies include decoder and encoder context layouts, waitqueues, and common interrupt constants.

## Integration Points
Called by codec-specific decode/encode implementation files after hardware submission. Woken by parent or subdevice interrupt handlers.

## Risks
The type inference depends on decoder/encoder context first field layout. It returns generic -1 rather than standard errno. No bounds check is done on `hw_id`; callers must validate. Clearing condition after every wait can hide late status if incorrectly shared.

## Test Signals
Successful interrupt wake, timeout path, signal interruption, multiple hardware indexes, and lockdep/race testing around interrupt and wait paths.
