# sources/distributed-fs/ceph-client/drivers/hid/hid-u2fzero.c

Purpose: exposes U2F Zero and Nitrokey U2F auxiliary functionality as Linux LED and hardware RNG devices while keeping HIDRAW access for U2F operations.

Important APIs, types, and functions: `struct hw_revision_config` provides per-revision RNG and wink commands. `struct u2f_hid_msg` and `struct u2f_hid_report` model 64-byte U2F HID reports using broadcast CID. `struct u2fzero_device` owns HID/USB pointers, URB, LED classdev, hwrng, buffers, mutex, presence flag, and revision. `u2fzero_send()` serializes output reports. `u2fzero_recv()` submits the interrupt-in URB, sends a command, waits with timeout, and copies the response. `u2fzero_brightness_set()` triggers wink on nonzero brightness. `u2fzero_rng_read()` sends the RNG command and returns bounded response data. `u2fzero_fill_in_urb()` builds a dedicated interrupt URB from usbhid endpoints.

Control flow: probe rejects non-USB, devm-allocates state and buffers, parses HID, starts HIDRAW, prepares the URB, marks the device present, derives names from the hidraw minor, then registers LED and hwrng devices. Remove marks the device absent under lock, stops HID, poisons, and frees the URB.

State and persistence: runtime state is devm-managed except the explicit URB. The mutex serializes command/response buffers and URB use. `present` prevents RNG reads after disconnect. No persistent storage exists.

Dependencies and integration: depends on HIDRAW, hwrng, LED classdev, USB interrupt URBs, and usbhid internals. Matches Cygnal U2F Zero and Clay Logic Nitrokey U2F IDs.

Risks: `u2fzero_fill_in_urb()` return is ignored in probe, so failures could leave `dev->urb` unset before RNG use. Command serialization relies on one shared URB and buffers. Response validation is minimal but bounds copies by actual length, message length, and caller max.

Test signals: no KUnit tests. Validate `/sys/class/leds/u2fzero*`, `/dev/hwrng` registration, RNG reads, LED blink, disconnect during read, and Nitrokey command differences.
