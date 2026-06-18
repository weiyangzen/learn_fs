# sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts.c

Purpose: `egalax_ts.c` is an I2C multitouch driver for EETI eGalax controllers. It handles the controller's 10-byte report packets, supports five contact slots, wakes the controller through a GPIO edge, and sends a firmware-version query during probe.

Important APIs, types, and functions: `struct egalax_ts` holds the I2C client and input device. `egalax_ts_interrupt()` retries `i2c_master_recv()` on `-EAGAIN`, filters non-multitouch report modes, decodes state, ID, down/up, X/Y/Z, and reports one MT slot update. `egalax_wake_up_device()` temporarily requests the `wakeup` GPIO as high, drives it low, switches it to input, and releases it. `egalax_firmware_version()` sends a fixed vendor command. PM callbacks send suspend command or wake through GPIO.

Control flow: probe allocates state/input, wakes the controller, sends the firmware command, initializes ABS and MT parameters, requests a oneshot threaded IRQ, and registers input. Each IRQ handles one point event and uses `input_mt_report_pointer_emulation()` after slot update. Suspend either enables IRQ wake or sends a 10-byte sleep command; resume disables wake or toggles the wakeup GPIO.

State and persistence: no persistent state is kept beyond input slots. The wakeup GPIO is not retained; it is requested only when a falling edge is needed. Firmware version is requested but not parsed or exposed.

Dependencies and integration points: it depends on I2C, GPIO descriptor `wakeup`, input MT, IRQ wake, OF compatible `eeti,egalax_ts`, and platform IRQ configuration.

Risks: only one contact update is present per packet, so correctness depends on controller sending all slot state changes. Slot ID validation uses `id > MAX_SUPPORT_POINTS`, allowing ID 5 while slots were initialized for IDs 0..4. Pressure `z` is decoded but no ABS_MT_PRESSURE parameter is initialized/reported. The firmware command return only confirms send success.

Test signals: test wake GPIO pulse, firmware command send, EAGAIN retry limit, ignoring mouse/vendor reports, valid/invalid ID handling, MT slot down/up transitions, suspend command, and wake-capable IRQ behavior.
