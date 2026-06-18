# sources/distributed-fs/ceph-client/drivers/platform/surface/surface_platform_profile.c

Purpose: Registers Linux platform-profile support for Surface devices through the Surface Aggregator thermal/fan subsystem, letting userspace select low-power, balanced, balanced-performance, or performance modes.

Important APIs and types: `enum ssam_tmp_profile` and `enum ssam_fan_profile` define firmware values. `struct ssam_tmp_profile_info` parses the TMP response. `struct ssam_platform_profile_device` stores the SSAM device, registered profile device, and `has_fan`. Core operations are `ssam_tmp_profile_get/set()`, `ssam_fan_profile_set()`, conversion helpers, and `ssam_platform_profile_get/set()`.

Control flow: The SSAM device driver matches `SSAM_SDEV(TMP, SAM, 0x00, 0x01)`. Probe allocates state, reads the optional `has_fan` property, and registers `platform_profile_ops`. The platform-profile core calls `probe` to advertise supported choices, `profile_get` to query TMP mode, and `profile_set` to set TMP mode and, when present, the FAN profile.

State and persistence: Driver state is devm-managed and minimal. Selected performance/fan profiles persist in EC/SSAM firmware until changed, reset, or power state transitions. No local cache is maintained, so reads always query firmware.

Dependencies and integration points: Depends on `linux/platform_profile.h`, Surface Aggregator SSAM device APIs, and firmware properties that indicate fan support. It integrates with userspace through the common platform-profile sysfs ABI.

Risks: TMP and FAN firmware profile numbering intentionally differs, so conversion helpers must not be merged casually. If TMP set succeeds and FAN set fails, profile state can become partially applied. Unknown firmware profile values return `-EINVAL` and may hide new modes until mapped.

Test signals: Probe on supported Surface devices; platform-profile sysfs shows four choices; set/get round trips for all modes; fan-equipped devices issue both TMP and FAN commands; non-fan devices do not attempt FAN writes; error injection for SSAM command failures.
