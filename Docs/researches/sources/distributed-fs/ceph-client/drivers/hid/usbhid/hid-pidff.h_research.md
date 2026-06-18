# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hid-pidff.h

## Purpose

`hid-pidff.h` is the small public interface for the HID PID force-feedback helper. It declares the initialization functions used by HID drivers and centralizes quirk bits that alter `hid-pidff.c` behavior for imperfect PID descriptors.

## Important APIs, Types, And Data

- `HID_PIDFF_QUIRK_MISSING_DELAY` tells upload code to skip the PID start-delay field.
- `HID_PIDFF_QUIRK_MISSING_PBO` tells condition uploads to skip parameter block offset and limit condition upload to one axis.
- `HID_PIDFF_QUIRK_PERMISSIVE_CONTROL` allows device-control discovery even when the field logical minimum is not the expected `1`.
- `HID_PIDFF_QUIRK_FIX_CONDITIONAL_DIRECTION` forces conditional effects to a fixed east/wheel direction during `SET_EFFECT`.
- `HID_PIDFF_QUIRK_PERIODIC_SINE_ONLY` maps all periodic waveforms to PID sine.
- Missing negative coefficient, negative saturation, and deadband quirks permit condition effects on devices missing those fields.
- `hid_pidff_init()` initializes with no caller-supplied quirks; `hid_pidff_init_with_quirks()` initializes with a seed quirk mask.

## Control Flow

The header has no runtime control flow. At compile time it either exposes the two function prototypes when `CONFIG_HID_PID` is enabled, or defines both names as `NULL` when the PID helper is not built. Callers can therefore assign/probe these hooks conditionally without needing a separate stub implementation.

## State And Persistence Behavior

The file defines only constants and declarations. Runtime state lives in `hid-pidff.c`, especially in `struct pidff_device` and the input FF device.

## Dependencies And Integration Points

- Includes `<linux/hid.h>` for `struct hid_device`.
- Is included by `hid-pidff.c` and by HID drivers that want to initialize PID force feedback.
- The quirk bits are part of the contract between device-specific HID drivers and the generic PID FF helper.

## Risks And Edge Cases

- When `CONFIG_HID_PID` is disabled, the macro replacement with `NULL` changes the symbol from a callable function to a null expression. Call sites must not unconditionally call it in that configuration.
- Quirk semantics must remain synchronized with `hid-pidff.c`; adding a quirk here without implementation or changing a meaning in code would silently break device-specific users.

## Test Signals

- Build coverage should include both `CONFIG_HID_PID=y/m` and disabled configurations.
- Device-specific users of `hid_pidff_init_with_quirks()` should verify that the expected quirk bit reaches the active quirk mask logged by `hid-pidff.c`.
- Static analysis should confirm no disabled-config call path attempts to call the macro-expanded `NULL`.
