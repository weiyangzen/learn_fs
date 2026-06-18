# sources/distributed-fs/ceph-client/drivers/platform/x86/portwell-ec.c

Purpose: This Portwell embedded-controller driver exposes EC temperature/voltage sensors through hwmon, eight EC GPIOs through gpiolib, and an EC watchdog through the watchdog framework for boards such as NANO-6064.

Important APIs, types, and functions: `struct pwec_sensor_prop` describes label/register/scale metadata. `struct pwec_board_info` selects visible temp/input channels. `pwec_read()`/`pwec_write()` access fixed I/O space, while `pwec_read16_stable()` protects 16-bit ADC reads from rollover. GPIO methods implement get/set/direction reporting, watchdog methods implement start/stop/ping/set_timeout/get_timeleft, and `pwec_hwmon_ops` provides sensor values and labels.

Control flow: Module init checks DMI unless `force` is set, registers a platform driver, and creates a `portwell-ec` platform device carrying board-info data. Probe reserves I/O region `0xe300-0xe3ff`, verifies the firmware vendor string `PWG`, registers a GPIO chip, registers hwmon when reachable, sets the watchdog parent, and registers the watchdog. Suspend stops an active watchdog and resume restarts it.

State and persistence: Hardware state includes GPIO value/direction registers, watchdog enable and countdown registers, and ADC sensor registers. Software state is mostly static metadata and a single static `watchdog_device`. The watchdog timeout is retained in `ec_wdt_dev.timeout`; suspend/resume toggles the EC watchdog around sleep.

Dependencies and integration points: It integrates with DMI, platform devices, I/O port resource management, gpiolib, hwmon, watchdog, and PM sleep ops. The `force` parameter permits full sensor-channel exposure without DMI validation.

Risks and edge cases: EC access has no explicit lock around GPIO and watchdog/hwmon accesses, so concurrent read-modify-write GPIO operations could race. Direction changing is deliberately unsupported because of board issues. A static watchdog device limits the design to one instance. Forced load on non-Portwell hardware can touch fixed I/O ports after only the firmware-vendor check. Suspend stopping an active watchdog may weaken expected watchdog coverage during sleep.

Test signals: Verify DMI-gated and forced probe, vendor string rejection, hwmon labels/scale calculations, stable ADC read behavior under changing registers, GPIO get/set for eight pins without direction changes, watchdog timeout range and timeleft stability, and watchdog restart after suspend/resume.
