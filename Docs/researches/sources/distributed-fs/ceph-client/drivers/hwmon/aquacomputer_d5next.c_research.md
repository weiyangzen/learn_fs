# sources/distributed-fs/ceph-client/drivers/hwmon/aquacomputer_d5next.c

## Purpose
This HID hwmon driver supports many Aquacomputer USB cooling devices, including D5 Next, Farbwerk, Farbwerk 360, Octo, Quadro, High Flow Next, Aquaero, Aquastream Ultimate/XT, Leakshield, Poweradjust 3, and High Flow USB/MPS Flow devices. It converts HID status and feature reports into hwmon temperature, fan, PWM, voltage, current, power, and debugfs information.

## Important APIs, Types, And Functions
`struct aqc_data` stores HID device handles, kind-specific report IDs and offsets, control report buffers and CRC parameters, counts and offsets for sensors, labels, cached readings, serial/firmware/power-cycle values, and update timestamp. `aqc_probe()` is the large product-ID dispatch that fills this structure for each device family. `aqc_raw_event()` processes periodic status report ID `0x01` for modern devices. Legacy devices use `aqc_legacy_read()` to request feature reports on demand.

Hwmon is implemented through `aqc_is_visible()`, `aqc_read()`, `aqc_read_string()`, and `aqc_write()`. Control report helpers `aqc_get_ctrl_data()`, `aqc_send_ctrl_data()`, `aqc_get_ctrl_val()`, `aqc_set_ctrl_val()`, and `aqc_set_ctrl_vals()` read-modify-write HID feature reports, adding CRC-16/USB where needed and sending the vendor secondary report after writes.

## Control Flow And State
Probe parses and starts HID, opens the device, filters composite Aquaero and Leakshield interfaces, configures offsets/labels/report sizes by product ID, allocates the control/status buffer, registers hwmon, and creates debugfs files for serial, firmware, and power cycles when offsets exist. Modern devices asynchronously update cached sensor values through `raw_event`; reads fail with `-ENODATA` when data is older than `STATUS_UPDATE_INTERVAL`. Legacy devices refresh synchronously during reads.

Writable state lives in device feature reports: temperature offsets, fan/PWM presets, flow pulses, and Aquaero fan preset routing. The in-memory cache stores the most recent sensor report and timestamps. Control report operations are rate-limited using `last_ctrl_report_op` and `ctrl_report_delay`, but there is no explicit mutex around buffer reuse, so concurrent writes could interleave.

## Dependencies And Integration Points
The driver integrates with HID raw requests/events, hwmon with-info APIs, debugfs, `crc16`, unaligned endian helpers, and the USB HID product table. It uses `late_initcall()` so registration happens after HID bus initialization.

## Risks
The main risks are product-specific offset drift, composite-interface misidentification, stale caches before the first report, concurrent control report buffer mutation, and device-specific checksum or secondary-report requirements. Several readings use sentinel `0x7fff` as `-ENODATA`; callers must handle that. Writes intentionally mimic vendor software but can alter pump/fan behavior.

## Test Signals
Test product-ID probe for every supported kind, Aquaero and Leakshield filtering, raw event parsing with N/A sensors, stale read behavior, legacy feature report refresh, control report CRC placement, secondary report emission, PWM percent conversion, temp offset clamping, flow pulse clamping, labels for special channels, debugfs file presence, and remove cleanup of debugfs/hwmon/HID resources.
