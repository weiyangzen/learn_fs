# sources/distributed-fs/ceph-client/drivers/hwmon/corsair-psu.c

Purpose: HID hwmon driver for Corsair HXi/RMi/HX-series PSUs with a proprietary sensor protocol. It reports input/output voltages, currents, power, temperatures, fan RPM/PWM, and selected critical thresholds, plus debugfs metadata and uptime.

Important APIs, types, and functions: `corsairpsu_data` stores HID/hwmon/debugfs pointers, completion, command buffer, vendor/product strings, cached critical thresholds, support bitmasks, and input-current command support. `corsairpsu_usb_cmd()` sends a 64-byte report, waits for a raw-event completion, validates command echo, and copies reply data. `corsairpsu_request()` selects rails before rail-specific commands. `corsairpsu_get_value()` handles little-endian reply assembly and LINEAR11 conversion. `corsairpsu_get_criticals()` and `corsairpsu_check_cmd_support()` populate feature state. `corsairpsu_hwmon_ops_*` implement visibility, reads, and labels.

Control flow: late init registers the HID driver. Probe parses/starts/opens HID, initializes completion, starts HID I/O, sends the special init command, queries firmware strings, probes thresholds and supported commands, registers `corsairpsu`, and initializes debugfs. Each hwmon read sends the appropriate PSU command, selecting a rail first when needed. Debugfs reads uptime, total uptime, vendor, product, and OCP mode. Resume reissues the init command because some PSUs power down the controller in standby.

State and persistence: threshold values and support bitmasks are cached at probe. Current sensor values are not cached. The driver is read-only for hwmon; it deliberately does not expose OCP mode switching because it is considered dangerous. Resume restores only protocol initialization, not cached threshold refresh.

Dependencies and integration points: depends on HID reports/raw events, hwmon channel info, debugfs, completions, PM resume hooks, and LINEAR11 conversion for PMBus-like values. Supported products are listed by USB VID/PID.

Risks: there is no mutex around `cmd_buffer` and completion use, so concurrent hwmon/debugfs reads can race command/response state. Hidraw is available by raw events and can interfere similarly. Visibility for temp channel 0 exposes `temp_crit` even though support bit checks apply only channel > 0, so unsupported critical values may appear as zero. Command support differs by PSU class, and unsupported commands are detected by echo mismatch. LINEAR11 conversion and rail selection must be correct to avoid misleading units.

Test signals: test all listed product IDs where possible, unsupported command handling, rail-specific values and labels, cached critical visibility, debugfs uptime/vendor/product/OCP mode, suspend/resume init, and concurrent reads from hwmon plus debugfs/hidraw. Unit checks should compare volts/currents/power/fan values against vendor tools.
