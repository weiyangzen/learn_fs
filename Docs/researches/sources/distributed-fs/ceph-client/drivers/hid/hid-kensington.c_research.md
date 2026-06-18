# sources/distributed-fs/ceph-client/drivers/hid/hid-kensington.c

## Purpose

`hid-kensington.c` supplies input mappings for Kensington Slimblade Trackball vendor-page button usages. It converts two Microsoft/vendor-page usages into standard mouse button codes so userspace sees middle and side buttons.

## Important APIs, Types, and Functions

- `ks_input_mapping(...)`: handles `HID_UP_MSVENDOR` usages `0x01` and `0x02`, mapping them to `BTN_MIDDLE` and `BTN_SIDE`.
- `ks_map_key(c)`: small wrapper around `hid_map_usage`.
- `ks_devices`: matches `USB_DEVICE_ID_KS_SLIMBLADE`.
- `ks_driver`: registers the input-mapping hook.

## Control Flow

During generic HID input setup, only Microsoft/vendor-page usages are considered by this driver. Usage `0x01` becomes `BTN_MIDDLE`; usage `0x02` becomes `BTN_SIDE`; all other usages fall through to generic mapping.

## State and Persistence Behavior

No driver-private state is allocated. The only persistent effect is the input capability and per-usage mapping stored by generic HID input setup.

## Dependencies and Integration Points

The file integrates with `hid-input.c` through `input_mapping`, uses HID/input constants, and matches the Kensington Slimblade USB ID from `hid-ids.h`.

## Risks and Edge Cases

- The mapping is device-specific but still assumes the vendor-page usage meanings stay stable for that PID.
- Unknown vendor usages fall through rather than being suppressed, so generic fallback behavior may still expose unexpected miscellaneous events.

## Test Signals

On a Slimblade Trackball, middle and side physical controls should emit `BTN_MIDDLE` and `BTN_SIDE`. Descriptor replay should verify non-MSVENDOR usages are unchanged and unknown MS vendor usages do not break probe.
