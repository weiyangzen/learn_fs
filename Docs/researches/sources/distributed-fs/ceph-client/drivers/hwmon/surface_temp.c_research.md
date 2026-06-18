
# sources/distributed-fs/ceph-client/drivers/hwmon/surface_temp.c

Purpose: Surface System Aggregator Module hwmon driver for firmware-provided thermal sensors. It exposes up to 16 labeled temperature channels.

Important APIs, types, and functions: `ssam_tmp_get_available_sensors()` reads a 16-bit availability bitmask. `ssam_tmp_get_temperature()` requests channel temperatures and converts firmware units from tenths Kelvin to millidegrees Celsius. `ssam_tmp_get_name()` fetches fixed-size sensor names and rejects non-terminated strings. `struct ssam_temp` stores the SSAM device, bitmask, and channel names. HWMON callbacks gate visibility by the bitmask, read temperatures, and return labels.

Control flow, state, and persistence: probe reads available sensors, allocates state, fetches labels for every set bit using channel IDs offset by one, and registers `surface_thermal`. There is no temperature cache; labels and availability are captured at probe.

Dependencies and integration points: depends on the Surface Aggregator device bus/controller, SSAM TMP target category commands, hwmon info API, and thermal-zone registration flag.

Risks and test signals: firmware name formatting is validated strictly; bad strings fail probe. Availability changes after probe are not reflected. Test bitmask visibility, Kelvin-to-Celsius conversion including negative Celsius values, label fetch errors, all 16 channel slots, and SSAM command failures during probe and reads.
