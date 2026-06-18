# sources/distributed-fs/ceph-client/drivers/hwmon/asus_rog_ryujin.c

Purpose: HID hwmon driver for the ASUS ROG Ryujin II 360 AIO cooler. It reports coolant temperature, pump/internal/controller fan speeds, and exposes writable PWM duty controls for pump, internal fan, and controller fans.

Important APIs, types, and functions: `rog_ryujin_data` stores HID device pointers, hwmon device, completions for each command/response class, cached temp/speed/duty arrays, a shared report buffer, and update timestamp. `rog_ryujin_execute_cmd()` reinitializes a selected completion under `status_report_request_lock`, sends a padded output report, and waits up to `STATUS_VALIDITY`. `rog_ryujin_get_status()` sequences four GET commands. `rog_ryujin_raw_event()` parses response headers and updates cached arrays. `rog_ryujin_read()`, `rog_ryujin_read_string()`, and `rog_ryujin_write()` implement hwmon callbacks.

Control flow: late init registers the HID driver for ASUS vendor/product IDs. Probe parses and starts HID with hidraw enabled, opens the device, allocates the report buffer, initializes completions, and registers `rog_ryujin` hwmon. A read refreshes all status groups when the 1.5-second cache expires. A PWM write for pump/internal fan first reads current cooler duty because those two values are set in one command, modifies one field, and waits for a set completion; controller fan duty writes directly.

State and persistence: temperature, RPM, and duty values are cached in memory until the refresh window expires. The driver does not persist settings across unload or suspend. After controller-duty writes, `duty_input[channel]` is pinned to the requested value until the next refresh. Completions represent in-flight command state and are also affected by hidraw traffic.

Dependencies and integration points: depends on HID output reports/raw events, hwmon core, completions, spinlocks, jiffies, and unaligned little-endian loads. It deliberately enables `HID_CONNECT_HIDRAW` so existing user-space tools can coexist, although that increases response ambiguity.

Risks: the protocol has ambiguous zero-duty reports because the device uses zero fields as write acknowledgements; the driver tries to distinguish expected read versus write completions. Concurrent hidraw users can trigger raw events and complete requests, so the spinlock/reinit scheme is critical. No mutex serializes all command sequences, so overlapping sysfs reads/writes could interleave commands. Channel 2 set command stores raw PWM while cooler channels convert to percent, so conversion consistency is a regression risk.

Test signals: test with actual Ryujin II 360 hardware, reading all labels and channels, writing 0/255/mid PWM values to each channel, and running concurrent hidraw traffic. Verify timeout behavior when the device is unplugged or silent, zero-duty read/write ambiguity, and cleanup through `hid_hw_close()`/`hid_hw_stop()`.
