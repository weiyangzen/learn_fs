
# sources/distributed-fs/ceph-client/drivers/hwmon/surface_fan.c

Purpose: Surface System Aggregator Module hwmon driver exposing Surface fan RPM as `fan1_input`.

Important APIs, types, and functions: `SSAM_DEFINE_SYNC_REQUEST_CL_R(__ssam_fan_rpm_get, __le16, ...)` defines the synchronous controller request for target category FAN command 0x01. `surface_fan_hwmon_read()` retrieves the `ssam_device` from driver data, sends the request, converts little-endian RPM, and returns it through hwmon. The channel info declares one fan input with fixed read-only visibility.

Control flow, state, and persistence: probe directly registers `surface_fan` with hwmon info using the SSAM device as driver data. There is no cache, no writable state, and no persistence. Each read synchronously asks firmware.

Dependencies and integration points: depends on Surface Aggregator device bus and controller request helpers, SSAM device id `SSAM_SDEV(FAN, SAM, 0x01, 0x01)`, and hwmon core. Probe is marked asynchronous-preferred.

Risks and test signals: user reads block on SSAM command completion and propagate firmware errors. Test SSAM match/probe, little-endian conversion, command failure propagation, repeated reads, and behavior when firmware reports zero RPM.
