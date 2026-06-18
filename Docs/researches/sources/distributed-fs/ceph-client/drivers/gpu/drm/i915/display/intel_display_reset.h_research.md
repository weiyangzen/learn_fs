# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_reset.h

## Purpose
This header declares the display reset prepare/finish API used by the wider driver reset path. It also defines the callback type used when reset preparation detects a potentially stuck modeset.

## Important APIs, Types, and Functions
The exported type is `typedef void modeset_stuck_fn(void *context)`. The public functions are `intel_display_reset_test(struct intel_display *display)`, `intel_display_reset_prepare(struct intel_display *display, modeset_stuck_fn modeset_stuck, void *context)`, and `intel_display_reset_finish(struct intel_display *display, bool test_only)`.

## Control Flow
The header has no executable logic. It documents the call pairing implicitly: reset code calls `intel_display_reset_prepare()` before the reset and, when it returns true, calls `intel_display_reset_finish()` afterward with the test-only decision from the reset owner.

## State and Persistence Behavior
No state is stored in this header. The API manages state in `struct intel_display`, especially the reset acquire context and saved modeset state.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and includes `<linux/types.h>` for `bool`. Integration points are higher-level GT/GPU reset code, display reset implementation, and any test path that forces modeset reset coverage.

## Risks
The boolean return from `intel_display_reset_prepare()` is a cleanup contract. A caller that ignores it can either leak locks or call finish unnecessarily. The callback must be safe in reset context because it is used to break a possibly stuck modeset before locks are acquired.

## Test Signals
Build coverage should catch signature drift. Runtime signals include reset paths pairing prepare/finish correctly, forced test-only reset restoring modesets, and no lockdep reports around reset.
