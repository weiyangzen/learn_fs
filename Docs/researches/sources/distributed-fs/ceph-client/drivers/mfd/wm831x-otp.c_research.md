# sources/distributed-fs/ceph-client/drivers/mfd/wm831x-otp.c

`wm831x-otp.c` exposes the WM831x 16-byte one-time-programmed unique ID through a read-only sysfs attribute and contributes it to kernel randomness during initialization.

Key functions are `wm831x_unique_id_read()`, `unique_id_show()`, `wm831x_otp_init()`, and `wm831x_otp_exit()`. The reader fetches eight 16-bit registers from `WM831X_UNIQUE_ID_1` onward and packs them into a byte array. The sysfs show function prints a no-separator hex string. Init creates `unique_id`, reads the UUID, and calls `add_device_randomness()` on success; exit removes the sysfs attribute.

Persistent state is the OTP hardware ID and the created device attribute. The driver stores no cached ID. Dependencies include WM831x core register helpers, OTP definitions, Linux device attributes, and randomness APIs.

Risks: sysfs read failure returns 0 bytes rather than a negative error; init logs sysfs creation failure but may still return UUID read status; the unique hardware identifier is exposed to userspace. Test signals include presence and format of the `unique_id` file, UUID read failure injection, and entropy contribution during probe.
