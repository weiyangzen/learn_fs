<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c -->
# sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c

## Purpose
`i2c-hid-core.c` implements the transport-independent HID-over-I2C protocol core. It owns descriptor fetch and validation, command formatting, interrupt-driven input reads, HID report get/set/send paths, reset sequencing, runtime/system power transitions, and registration of the HID low-level driver. Thin ACPI/OF/vendor wrappers provide power callbacks and the HID descriptor address; this file turns those callbacks plus an `i2c_client` into a normal `hid_device`.

## Important APIs, Types, and Functions
The persistent `struct i2c_hid` stores the I2C client, HID device, parsed HID descriptor, descriptor-register address, command/input/raw buffers, flags, quirks, waitqueue, command/reset mutexes, wrapper `i2chid_ops`, and optional DRM panel-follower state. `i2c_hid_desc` is the packed on-wire HID descriptor. Exported entry points are `i2c_hid_core_probe`, `i2c_hid_core_remove`, `i2c_hid_core_shutdown`, and `i2c_hid_core_pm`.

Protocol helpers include `i2c_hid_xfer`, `i2c_hid_read_register`, `i2c_hid_encode_command`, `i2c_hid_get_report`, `i2c_hid_set_or_send_report`, `i2c_hid_set_power`, `i2c_hid_start_hwreset`, and `i2c_hid_finish_hwreset`. HID core callbacks are supplied through `i2c_hid_ll_driver`: parse, start, stop, open, close, output report, and raw request. Input handling is driven by `i2c_hid_irq` and `i2c_hid_get_input`.

## Control Flow
Probe validates IRQ presence, allocates `struct i2c_hid`, initializes locks/work/waitqueue, allocates minimum buffers, allocates a HID device, and either powers/probes immediately or registers as a DRM panel follower. The direct probe path powers rails through `ops->power_up`, probes the I2C address, fetches the HID descriptor or DMI override, validates descriptor version/length, copies VID/PID into `hid_device`, merges DMI quirks, requests the IRQ, enables it, and calls `hid_add_device`.

HID parse resets the device with retry, then obtains the report descriptor through a DMI override or descriptor-register read before calling `hid_parse_report`. Start recomputes buffer size from parsed input/output/feature reports and reallocates with the IRQ disabled if needed. Interrupt handling reads `wMaxInputLength` bytes, treats zero-length input as reset completion, filters bogus `0xffff` IRQs, validates report length, optionally fixes known bad sizes, and forwards reports through `hid_safe_input_report` only while the HID device is opened.

Suspend calls `hid_driver_suspend`, optionally sends I2C-HID sleep, disables IRQ, and powers down when wakeup is not needed or forced. Resume powers up if required, enables IRQ, optionally delays Goodix wakeup, resets selected devices, otherwise sends power-on, then calls `hid_driver_reset_resume`. Panel followers perform probe/resume asynchronously from panel prepare/enable callbacks and suspend/power-down from panel unprepare/disable.

## State and Persistence Behavior
Persistent state is per I2C client and devm-owned except buffers and `hid_device`, which are explicitly freed/destroyed. `I2C_HID_STARTED` gates input delivery, and `I2C_HID_RESET_PENDING` synchronizes reset IRQ completion with `wait_event_timeout`. `cmd_lock` serializes shared command/raw buffers; `reset_lock` prevents feature report transfers from racing a reset and losing reset-complete interrupts. Device quirks persist after descriptor parsing and affect reset, suspend, wakeup, bogus IRQ, and report-size behavior. Panel-follower state uses workqueue memory barriers to decide whether a suspend callback should power down a successfully powered device.

## Dependencies and Integration Points
The file depends on Linux I2C transfers, IRQ threads, HID core, PM/wakeup, mutex/waitqueue APIs, DRM panel follower support, DMI override helpers from `i2c-hid-dmi-quirks.c`, and wrapper-provided `i2chid_ops` from OF/vendor drivers. It integrates with HID generic/multitouch/RMI consumers through `hid_add_device`, with wake IRQ policy through `device_may_wakeup`, and with board-specific power sequencing through optional callbacks.

## Risks and Edge Cases
The driver trusts descriptor register fields after basic size/version checks; bad register offsets or max lengths can cause failed transfers or buffer-pressure paths. `i2c_hid_set_or_send_report` checks `data_len > ihid->bufsize` before adding command/report-id overhead, so command buffer sizing must stay aligned with max report computation. Reset completion relies on devices sending an IRQ unless the no-IRQ quirk is set. Panel-follower paths require careful ordering because HID device registration may happen after core probe. Goodix, ELAN, QTEC, ALPS, Raydium, SIS, and other quirks show that small timing or power-sequence changes can regress specific hardware.

## Test Signals
Useful signals include successful descriptor/report parsing, HID device creation, input events after open, raw GET/SET feature report behavior, suspend/resume with and without wakeup, reset-on-resume devices, DMI descriptor overrides, panel-follower power ordering, no IRQ storms, no reset timeouts, no incomplete reports, and lockdep-clean operation across IRQ, reset, and raw request paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/i2c-hid/i2c-hid-core.c -->
