# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctma140.c

Purpose: `cy8ctma140.c` is an I2C driver for Cypress CY8CTMA140/TMA140 multitouch controllers. It assumes firmware is already present in controller flash, reads up to four contacts from fixed-format I2C packets, and exposes a direct multitouch input device.

Important APIs, types, and functions: `struct cy8ctma140` holds the `input_dev`, touchscreen properties, `i2c_client`, two regulators (`vcpin`, `vdd`), and legacy previous-finger fields. `cy8ctma140_irq_thread()` sends command `CY8CTMA140_GET_FINGERS` then reads a 31-byte packet with `i2c_transfer()`. `cy8ctma140_report()` maps controller contact IDs to MT slots with `input_mt_get_slot_by_key()`, decodes big-endian X/Y and width, applies `touchscreen_report_pos()`, and reports `ABS_MT_TOUCH_MAJOR`. `cy8ctma140_init()` fetches firmware info. Power helpers bulk-enable/disable regulators, with simple PM ops around suspend/resume.

Control flow: probe allocates the state and input device, sets ABS capabilities and touchscreen properties, initializes four MT slots with `INPUT_MT_DIRECT | INPUT_MT_DROP_UNUSED`, obtains regulators, powers up with a 250 ms delay, registers a devm power-off action, requests a oneshot threaded IRQ, reads firmware info, then registers input. The IRQ path validates transfer count, drops packets marked invalid by bit 5 of `buf[1]`, validates finger count, and reports current contacts.

State and persistence: the only durable state is regulator power state and input slot tracking maintained by the input core. The driver reads firmware metadata but does not update firmware or persist settings. Suspend powers the controller down unless the device is wake-capable.

Dependencies and integration points: it depends on standard I2C transfers, regulator supplies named `vcpin` and `vdd`, DT compatible `cypress,cy8ctma140`, and touchscreen properties for axis ranges. The input integration is type-B multitouch; DT should provide required axis properties because the driver intentionally does not default X/Y maxima.

Risks: the packet parser relies on hard-coded offsets and split contact-ID nibbles, so firmware format mismatches can silently drop contacts. Probe requests the IRQ before registering input, so spurious early IRQs depend on hardware readiness. Touch-key bytes in the packet are not handled. Wakeup suspend leaves power on but no explicit wake IRQ programming is done here.

Test signals: validate regulator sequencing, firmware info read, invalid-packet suppression, contact ID to slot reuse, 1 to 4 finger reports, axis inversion/swap DT properties through `touchscreen_parse_properties()`, and suspend/resume both with and without `device_may_wakeup()`.
