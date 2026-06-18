# sources/distributed-fs/ceph-client/drivers/watchdog/geodewdt.c

## Purpose
This legacy watchdog driver supports AMD Geode GX/LX systems using the CS5535/CS5536 MFGPT timer reset event. It exposes a miscdevice `/dev/watchdog` interface.

## Important APIs, types, and functions
Global state includes platform device pointer, open/orphan flags, `cs5535_mfgpt_timer`, timeout, and safe-close flag. Hardware helpers are `geodewdt_ping`, `geodewdt_disable`, and `geodewdt_set_heartbeat`. File operations implement write, ioctl, open, and release. Platform callbacks include probe, remove, and shutdown.

## Control Flow
Module init creates a platform device and probes the driver. Probe allocates an MFGPT timer, configures scale and reset-on-CMP2 event, sets the initial compare value, and registers `/dev/watchdog`. Open enforces single-open, handles orphaned nowayout state, and pings. Writes scan for magic close and ping. Ioctls support options, keepalive, and timeout get/set. Unexpected close marks the device orphaned and leaves the timer running.

## State and Persistence
Runtime state is entirely global. MFGPT hardware retains compare/setup state until disabled or reset. Orphan flag tracks an unexpected close while keeping module references consistent.

## Dependencies and Integration Points
The driver depends on CS5535 MFGPT APIs, platform-device self-registration, miscdevice watchdog ABI, reboot/shutdown callback, and module timeout/nowayout parameters.

## Risks and Test Signals
Risks include timer allocation failure, module reference/orphan handling, timeout range limits, reset-event configuration, and lack of watchdog core supervision. Tests should cover safe and unsafe close, reopen after orphan, timeout boundaries, shutdown disable, ioctl options, and MFGPT API failure paths.
