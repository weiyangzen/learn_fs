# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-wmax.c

Purpose: Newer Alienware WMAX/AWCC backend. It handles WMAX AlienFX LEDs and optional HDMI, amplifier, deep-sleep, AWCC hwmon, fan boost, platform thermal profile, G-Mode, GPIO debugfs, and PM restore behavior.

Important APIs/types/functions: WMAX LED/brightness methods, AWCC wrappers (`awcc_wmi_command`, `awcc_thermal_information`, `awcc_op_*`), `struct awcc_priv`, hwmon callbacks, platform-profile callbacks, debugfs helpers, `alienware_awcc_setup()`, and `wmax_wmi_probe()`.

Control flow/state/persistence: Init selects AWCC quirks from DMI or unsafe force parameters, then registers the WMI driver. Probe initializes AWCC services if quirks are present; otherwise it uses the base AlienFX platform setup. AWCC setup reads system description, validates resource counts, builds sensor/profile mappings, registers hwmon/profile devices, and creates debugfs. Firmware stores active profile and fan state; driver caches mappings and suspend fan-boost values.

Dependencies/integration: Alienware base, ACPI WMI, DMI, hwmon, platform_profile, PM, debugfs, and sysfs groups exported through `alienware-wmi.h`.

Risks/test signals: Firmware may report malformed resource/profile counts; force parameters bypass normal checks. Test quirked machines, forced hwmon/profile modes, sensor labels/readings, fan boost clamp and suspend/resume restore, profile mapping/G-Mode toggling, and debugfs GPIO.
