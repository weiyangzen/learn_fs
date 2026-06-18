# sources/distributed-fs/ceph-client/drivers/platform/x86/silicom-platform.c

Purpose: This Silicom MEC170x platform driver supports Cordoba network appliances. It exposes multicolor front-panel LEDs, named GPIOs, fan speed, temperature, and sysfs controls/status for MEC efuse, firmware version, and power-cycle command through fixed I/O ports.

Important APIs, types, and functions: `struct silicom_platform_info` holds DMI-selected platform wiring. `silicom_mec_port_get()` and `silicom_mec_port_set()` perform indirect MEC I/O under `mec_io_mutex`. Multicolor LED callbacks map subled channels to active-low MEC bits. GPIO callbacks expose named channels and enforce direction based on register offset. `silicom_mc_leds_register()` deep-copies `__initdata` LED descriptors into devm allocations. `silicom_fan_control_hwmon_ops` exposes fan/temp labels and values.

Control flow: DMI callbacks select the platform info and assign global initdata pointers. `silicom_platform_init()` requires a DMI match, then creates a bundled platform device/driver. Probe reserves MEC I/O ports, checks magic value `0x5a`, registers DMI-selected multicolor LEDs, registers the GPIO chip with channel map, and registers hwmon. Sysfs reads and writes perform indirect EC register selection and data access.

State and persistence: Hardware state lives in MEC I/O registers for GPIO/LED outputs, fan/temp readings, efuse status, uC version, and power-cycle command. Software globals cache `efuse_status`, `mec_uc_version`, `power_cycle`, and selected platform wiring pointers. All MEC access is serialized by `mec_io_mutex`.

Dependencies and integration points: It integrates with DMI, platform bundle creation, I/O port resource management, multicolor LED class, gpiolib, hwmon, sysfs attribute groups, bitfield helpers, and mutex-protected port I/O.

Risks and edge cases: Selected wiring pointers are marked `__initdata`; they are used during init/probe only and copied before init memory is freed, so ordering matters. GPIO direction is inferred from encoded channel offset and can reject legitimate direction changes if mappings are wrong. Active-low LED/GPIO output semantics differ between LED and GPIO paths and need careful validation. The `power_cycle` sysfs write triggers hardware reset behavior for any positive input.

Test signals: Test DMI variants `80300-0214-G`, `80500-0214-G`, and `80300-0222-G`; bad magic rejection; LED colors and active-low behavior; named GPIO input/output direction enforcement; fan RPM and temperature scaling; sysfs efuse/version/power-cycle; concurrent sysfs/GPIO/LED/hwmon access under the mutex; and module unload cleanup.
