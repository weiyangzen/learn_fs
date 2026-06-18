# sources/distributed-fs/ceph-client/Documentation/firmware_class/hotplug-script

## Purpose
`hotplug-script` is a sample firmware-class hotplug helper showing how userspace can satisfy kernel firmware requests through sysfs. It is documentation/example shell code, not a production in-kernel implementation.

## Important APIs, Types, and Functions
The script consumes environment variables `SUBSYSTEM`, `ACTION`, `DEVPATH`, and `FIRMWARE`, and uses the local `HOTPLUG_FW_DIR=/usr/lib/hotplug/firmware/`. Its external API is the firmware loader sysfs protocol: write `1` to `/sys/$DEVPATH/loading`, stream bytes to `/sys/$DEVPATH/data`, then write `0` for success or `-1` for failure.

## Control Flow
Control flow is a single guard: when `$SUBSYSTEM` is `firmware` and `$ACTION` is `add`, the script checks whether `$HOTPLUG_FW_DIR/$FIRMWARE` exists. If present, it marks loading active, copies the firmware file into the sysfs data attribute, and marks loading complete. If absent, it writes `-1` to cancel the kernel request.

## State and Persistence Behavior
The script keeps no durable state. It transiently changes firmware loader state under sysfs for the requesting device. The persistent input is the firmware file stored below `/usr/lib/hotplug/firmware/`; successful loading transfers its contents into the kernel requester.

## Dependencies and Integration Points
Depends on a POSIX-like shell, hotplug/udev environment variables, readable firmware files, and writable firmware-class sysfs attributes. It integrates with `request_firmware()` fallback behavior and user-mode helper policy.

## Risks
The sample uses unquoted variables and `==` in `/bin/sh`, so paths with whitespace or shells without that extension can misbehave. In production, firmware names must be sanitized, sysfs writes need error handling, and helper execution depends on kernel/user-mode-helper and distribution policy.

## Test Signals
Test with a controlled firmware request that sets `SUBSYSTEM=firmware`, `ACTION=add`, valid and missing `FIRMWARE` values, and a temporary sysfs-like directory. Verify the `loading` sequence is `1`, data bytes, `0` on success and `-1` on missing files.
