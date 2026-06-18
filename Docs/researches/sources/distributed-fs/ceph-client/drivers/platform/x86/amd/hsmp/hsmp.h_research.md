# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/hsmp.h

Purpose: `hsmp.h` is the internal HSMP header shared by the common core, ACPI front end, platform front end, and hwmon support.

Important APIs, types, and functions: it defines device names (`hsmp_cdev`, `hsmp`), ACPI HID `AMDI0097`, driver version, `struct hsmp_mbaddr_info`, `struct hsmp_socket`, and `struct hsmp_plat_device`. It declares common APIs for mailbox tests, ioctl handling, misc registration, metrics-table reads, protocol caching, socket singleton access, and `hsmp_msg_get_nargs()`. It conditionally declares or stubs `hsmp_create_sensor()` based on `CONFIG_HWMON`.

Control flow: not executable, but it defines how front ends populate socket read/write callbacks and how optional hwmon hooks compile away.

State and persistence: structures define runtime state but do not instantiate it. State includes MMIO addresses, metric-table mappings, semaphores, socket indices, protocol version, and misc-device status.

Dependencies and integration points: includes compiler, device, hwmon, kconfig, miscdevice, PCI, semaphore, and sysfs headers. It bridges kernel internal code to UAPI message definitions in `<asm/amd/hsmp.h>`.

Risks: because this header defines shared structures, ABI-like assumptions exist across objects. Changing fields can affect all front ends. The hwmon stub returns success, so callers must not assume a real sensor exists when `CONFIG_HWMON` is off.

Test signals: compile with and without `CONFIG_HWMON`, namespace exports using declared functions, and structure field consistency between ACPI/platform/common source files.
