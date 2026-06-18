# sources/distributed-fs/ceph-client/drivers/staging/greybus/bootrom.c

## Purpose

`bootrom.c` implements the Greybus Bootrom class driver that serves stage-2 firmware blobs to a module boot ROM, tracks the required request sequence, handles protocol version negotiation, and waits for mode switch after ready-to-boot.

## Important APIs, Types, and Functions

`struct gb_bootrom` stores connection, loaded firmware, negotiated protocol version, next expected request, delayed timeout work, and firmware mutex. Key helpers are `free_firmware()`, `gb_bootrom_timedout()`, timeout set/cancel, `bootrom_es2_fixup_vid_pid()`, `find_firmware()`, request handlers for firmware size/get firmware/ready-to-boot, `gb_bootrom_get_version()`, `gb_bootrom_probe()`, and `gb_bootrom_disconnect()`.

## Control Flow

Probe validates a single bootrom CPort, creates a Greybus connection with request handler, enables TX, negotiates protocol version, optionally fixes ES2 VID/PID through a bootrom request, enables the connection, arms a timeout for firmware-size request, and sends AP_READY. Firmware-size requests cancel the prior timeout, load the stage-2 firmware file based on DDBL and VID/PID IDs, respond with size, and arm a get-firmware timeout. Get-firmware requests validate offset/size, allocate a response, copy firmware bytes, and arm either another get timeout or ready-to-boot timeout. Ready-to-boot validates status and arms a longer mode-switch timeout.

## State and Persistence Behavior

The loaded firmware pointer persists only during a boot transaction and is released on timeout, disconnect, or new firmware lookup. Interface VID/PID may be modified in memory for ES2 devices with missing GMP IDs. No firmware is written to disk by this driver; firmware data is read from the kernel firmware loader and sent over Greybus.

## Dependencies and Integration Points

It depends on Greybus bundle/connection/operation APIs, Linux firmware loader, delayed work, mutexes, jiffies, and firmware naming constants from `firmware.h`. It registers as the Greybus bootrom class driver.

## Risks and Edge Cases

In `gb_bootrom_get_firmware()`, `offset`, `size`, and `fw` are used in the `queue_work` path even when payload-size validation fails before they are initialized, a strong bug signal. The timeout work frees firmware but does not power off the module. Firmware filename construction is fixed and stage support is hard-coded to stage 2. ES2 VID/PID fixup races with user-space reading sysfs IDs. Ready-to-boot status treats insecure firmware as success by design comment.

## Test Signals

Test protocol negotiation major mismatch, AP_READY failure, ES2 VID/PID fixup, missing firmware, bad stage, partial and final firmware reads, invalid offsets/sizes, malformed request sizes, timeout paths for each expected request, disconnect during delayed work, and mode-switch timeout after ready-to-boot.
