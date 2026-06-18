<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c

Purpose: implements the Congatec Board Controller core driver for selected x86 Congatec modules. It discovers supported boards by DMI, registers a platform device with fixed I/O-port resources, manages a controller session, exports a command transport helper, exposes firmware version through sysfs, and registers watchdog, GPIO, I2C, hwmon, and backlight children.

Important APIs and functions: exported command API is `cgbc_command`. Lifecycle functions are `cgbc_init`, `cgbc_exit`, `cgbc_probe`, and `cgbc_remove`. Session helpers include `cgbc_wait_device`, `cgbc_session_command`, `cgbc_session_request`, and `cgbc_session_release`; command-port locking helpers are `cgbc_command_lock` and `cgbc_command_unlock`. `cgbc_get_version` reads firmware revision using command `0x21`.

Control flow: module init checks the DMI table for conga-SA7 or conga-SA8, registers a synthetic platform device with session and command I/O-port ranges, then registers the driver. Probe maps both I/O-port windows, initializes a mutex, requests a valid controller session handle, queries firmware revision, and adds child devices. `cgbc_command` serializes access, locks the command interface with the session handle, waits for strobe readiness, writes command bytes plus XOR checksum in manual/auto modes, strobes execution, reads status/data/checksum, validates the response checksum, unlocks, and returns optional status.

State and persistence: `struct cgbc_device_data` holds device, mapped I/O windows, mutex, session handle, and firmware version. The controller session persists from probe until remove; child devices share the exported command helper and parent state. Hardware command/session state lives in fixed I/O ports.

Dependencies and integration points: depends on DMI matching, platform devices, I/O-port mapping, polling helpers, sysfs attributes, MFD core, and child drivers named `"cgbc-wdt"`, `"cgbc-gpio"`, two `"cgbc-i2c"` instances, `"cgbc-hwmon"`, and `"cgbc-backlight"`. Child drivers call `cgbc_command` to transact with the board controller.

Risks: module init registers the platform device before the platform driver and does not unregister it if driver registration fails. Fixed I/O-port ranges assume no conflicts. Command framing is timing-sensitive and uses short polling timeouts; firmware stalls produce transport errors. Response data larger than the caller buffer is truncated before checksum comparison, which can cause checksum mismatch or hide extra data depending on firmware behavior. Session release happens before `mfd_remove_devices` in remove, so child teardown must not issue commands after release.

Test signals: DMI-gated module load on supported/unsupported boards, I/O resource mapping, firmware version sysfs output, command checksum success/failure injection, concurrent child command serialization, watchdog/GPIO/I2C/hwmon/backlight child binding, and remove/unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cgbc-core.c -->
