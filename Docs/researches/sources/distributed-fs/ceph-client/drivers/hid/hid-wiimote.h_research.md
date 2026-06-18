# sources/distributed-fs/ceph-client/drivers/hid/hid-wiimote.h

## Purpose

`hid-wiimote.h` is the shared contract for the Wiimote driver. It defines protocol flags, report IDs, device and extension enums, persistent state structures, module ops, exported request helpers, debug hooks, and inline synchronous-command helpers.

## Important APIs, Types, and Functions

- `WIIPROTO_FLAG_*`: persistent protocol flags for LEDs, rumble, accelerometer, IR, extension, Motion Plus, exit, DRM lock, and Pro calibration.
- `enum wiimote_devtype`, `enum wiimote_exttype`, and `enum wiimote_mptype`: core classification values.
- `struct wiimote_queue`: output report ring protected by `queue.lock`.
- `struct wiimote_state`: spinlock-protected protocol state, synchronous command fields, cached command results, and calibration caches.
- `struct wiimote_data`: per-HID-device object that owns input/LED/battery/debug/timer/workqueue state.
- `struct wiimod_ops`: module callback interface for probe/remove and payload dispatch.
- `enum wiiproto_reqs`: native output/input/data report IDs and DRM variants.
- Inline command helpers: `wiimote_cmd_pending`, `wiimote_cmd_complete`, `wiimote_cmd_abort`, acquire/release, set, and timed wait helpers.

## Control Flow and API Contract

Callers that issue synchronous commands acquire `state.sync`, set command metadata under `state.lock`, send a request, wait on `state.ready`, and release the mutex. Report handlers complete or abort the command under the same spinlock. Module callbacks are invoked by core report handlers and may request DRM changes, input events, or module reconciliation through `__wiimote_schedule`.

## State and Persistence Behavior

This header centralizes long-lived state layout. `flags`, `drm`, `devtype`, `exttype`, `mp`, battery, calibration, and rumble caches survive across reports and module callbacks. `cmd_read_buf` points to caller-provided transient storage and must be cleared after waits. The completion provides the memory-ordering assumption used by wait helpers.

## Dependencies and Integration Points

It integrates Linux completion, HID, input, LED, power_supply, mutex, spinlock, and timer APIs. It is included by the core, debug, and module files and forms the ABI between those translation units.

## Risks and Edge Cases

- Several inline helpers require `state.lock` but cannot enforce it.
- `cmd_read_buf` is a raw pointer into caller storage; stale pointers after timeout/disconnect would be dangerous if not cleared.
- `WIIPROTO_FLAGS_IR` includes `WIIPROTO_FLAG_IR_FULL` even though full is the OR of basic and ext, so bitmask logic must preserve this encoding.
- Struct fields expose internals broadly, so unrelated files can mutate protocol state directly.

## Test Signals

- Build coverage for core/debug/modules catches function signature drift.
- Lockdep and KCSAN are useful around command helpers and report handlers.
- Timeout tests should confirm command waits return `-EIO` and do not leave reusable command state stuck.
- Module table changes should be validated against enum bounds and null dummy entries.
