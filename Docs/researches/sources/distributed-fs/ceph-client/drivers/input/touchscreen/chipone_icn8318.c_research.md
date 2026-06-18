# sources/distributed-fs/ceph-client/drivers/input/touchscreen/chipone_icn8318.c

Purpose: I2C multitouch driver for ChipOne ICN8318 controllers. It controls a wake GPIO, hibernates the chip when closed, reads up to five touch records on interrupts, and reports direct multitouch positions through the input subsystem.

Important APIs/types/functions: `struct icn8318_data` stores the I2C client, input device, wake GPIO, and touchscreen properties. Wire records are `struct icn8318_touch` and `struct icn8318_touch_data`. Key functions are `icn8318_read_touch_data()`, `icn8318_touch_active()`, `icn8318_irq()`, `icn8318_start()`, `icn8318_stop()`, `icn8318_suspend()`, `icn8318_resume()`, and `icn8318_probe()`.

Control flow: probe requires an IRQ and a `wake` GPIO, allocates input, sets MT position capabilities, parses common touchscreen properties and requires nonzero X/Y maxima, initializes five direct drop-unused slots, requests a threaded IRQ, immediately stops/hibernates the device until open, registers input, and stores client data. Open enables IRQ and asserts wake. Close disables IRQ, writes hibernate to the power register, and deasserts wake. IRQ reads the touch data block through a two-message I2C transfer, ignores softbutton events, clamps excessive touch counts, reports active slots for update events 2/3, marks end events inactive, syncs the MT frame, and syncs input.

State and persistence: there is no persistent configuration beyond wake GPIO and input properties. Device power mode is controlled by writes to `ICN8318_REG_POWER` and by wake GPIO state. Input open/close and PM callbacks share the input mutex.

Dependencies/integration: depends on I2C core, GPIO descriptors, input MT, common touchscreen property parsing, IRQ threading, OF compatible `chipone,icn8318`, and an empty I2C ID table required by the I2C subsystem.

Risks and test signals: `icn8318_read_touch_data()` returns the raw `i2c_transfer()` count; the IRQ only treats negative values as errors, so a short positive transfer would be processed as if successful. Stop writes hibernate after disabling IRQ and does not check the write result. Softbutton reports are ignored entirely. Test missing size properties, wake GPIO polarity, open/close IRQ balancing, suspend/resume while open, short I2C transfers, touch_count clamping, release event handling, and hibernate exit timing.
