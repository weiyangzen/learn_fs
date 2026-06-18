# sources/distributed-fs/ceph-client/drivers/hid/hid-axff.c

Purpose: adds force-feedback rumble support for ACRUX game controllers while leaving normal input handling to HID/input.

Important APIs/types/functions: `struct axff_device` stores the output report used for rumble. Under `CONFIG_HID_ACRUX_FF`, `axff_init()` locates the first HID input and first output report, zeroes all output fields, validates field count for most devices, sets `FF_RUMBLE`, and registers a memless force-feedback callback with `input_ff_create_memless()`. `axff_play()` scales strong/weak magnitudes from 16-bit input FF values to 8-bit report values and alternates left/right values across report fields. `ax_probe()` parses and starts the device with generic FF disabled, initializes custom FF, and opens the HID device to keep polling active. `ax_remove()` closes and stops hardware.

Control flow: probe calls `hid_parse()`, `hid_hw_start(HID_CONNECT_DEFAULT & ~HID_CONNECT_FF)`, attempts `axff_init()`, warns rather than failing if FF setup fails, then calls `hid_hw_open()` because the controller otherwise stops producing reports. The input FF core later calls `axff_play()` for rumble effects, which updates the cached output report and submits `HID_REQ_SET_REPORT`.

State/persistence: per-device FF state is a small heap allocation attached as the memless FF private data. Rumble state lives in HID report field values and on the device after each set-report. No persistent settings are stored by the driver.

Dependencies/integration: depends on HID core report parsing/request APIs, Linux input FF memless support, `CONFIG_HID_ACRUX_FF`, and ACRUX USB IDs.

Risks: `axff_init()` assumes the first output report layout corresponds to rumble channels. The memless private allocation is not explicitly freed in this driver and relies on input FF/device teardown. Always opening the HID device increases lifecycle sensitivity: remove must close if open succeeded. FF setup failure is nonfatal, so tests must inspect warnings as well as probe return.

Test signals: verify controller input still works without FF, rumble produces expected left/right strength, product `0xf705` tolerates fewer than four fields, probe failure after `hid_hw_open()` closes/stops hardware, and builds with `CONFIG_HID_ACRUX_FF=n` still bind without FF.
