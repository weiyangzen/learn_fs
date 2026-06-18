# sources/distributed-fs/ceph-client/drivers/hid/hid-generic.c

Provides the fallback generic HID driver for devices not claimed by a more specific driver. It parses descriptors, starts standard HID hardware/input plumbing, and defers to special drivers when appropriate.

`hid_generic_match()` is the central policy hook. It honors `ignore_special_driver`, `HID_QUIRK_IGNORE_SPECIAL_DRIVER`, and `HID_QUIRK_HAVE_SPECIAL_DRIVER`, then scans `hid_bus_type` with `bus_for_each_drv()` and `__check_hid_generic()` to see if another driver matches. `hid_generic_probe()` sets `HID_QUIRK_INPUT_PER_APP`, parses, and starts `HID_CONNECT_DEFAULT`. `hid_generic_reset_resume()` resets input state when input was claimed.

The broad match table accepts any HID bus/group/vendor/product, so `.match` carries the binding policy. State is limited to in-memory quirks and HID claim state; nothing persists. Dependencies include HID core, driver bus iteration, and input reset-resume support.

Risks are incorrect arbitration that either steals devices from specialized drivers or leaves devices unbound. Test signals include generic-only devices, devices with special drivers, the two special-driver quirks, reset-resume with claimed input, and module registration ordering.
