# sources/distributed-fs/ceph-client/drivers/hwmon/corsair-cpro.c

Purpose: HID hwmon driver for Corsair Commander Pro and Corsair 1000D controllers. It exposes connected temperature probes, fan RPMs, fan PWM/target controls, and voltage rails while keeping hidraw access available.

Important APIs, types, and functions: `ccp_device` stores HID/hwmon/debugfs pointers, command and response buffers, completion/spinlock for report waits, a mutex serializing command buffer usage, fan target cache, connection bitmaps, labels, and firmware/bootloader versions. `send_usb_cmd()` builds 63-byte output reports, reinitializes completion under spinlock, sends the command, waits for a 16-byte response, and maps device status bytes via `ccp_get_errno()`. `ccp_raw_event()` copies one pending input report. `get_data()`, `set_pwm()`, and `set_target()` implement common protocol operations. Probe reads connection status and versions before hwmon registration.

Control flow: late init registers the HID driver. Probe allocates buffers, parses/starts/opens HID with hidraw, initializes synchronization, starts HID I/O, reads temp and fan connection bitmaps, creates debugfs version files, and registers `corsaircpro`. Visibility depends on connection bitmaps. Reads send command-per-value requests; writes convert PWM 0-255 to device percent or set fan target RPM. Fan target reads return only the last value set by this driver.

State and persistence: connection status is sampled once at probe and does not update until reprobe. Firmware/bootloader versions are cached for debugfs. `target[channel]` is a software-only cache initialized to `-ENODATA` and invalidated by fixed PWM writes. Hardware fan settings persist in the device until changed, but the driver does not restore state.

Dependencies and integration points: depends on HID output reports/raw events, hwmon info API, debugfs, completions, mutexes, spinlocks, and bitmaps. Hidraw remains enabled, and comments note simultaneous userspace may switch reports.

Risks: hidraw concurrency can consume or inject reports for the driver's pending command. Connection status is only accurate at power-on/probe. Reads have no caching, so frequent polling issues many HID commands. Fan target readback is not supported by protocol and may mislead users after external changes. Error code mapping depends on the first response byte only.

Test signals: test Commander Pro and 1000D IDs, connected/disconnected temp and fan channels, 3-pin/4-pin labels, PWM endpoint conversion, target writes/readbacks, voltage rails, debugfs version files, timeout and wrong-size report handling, and concurrent hidraw traffic.
