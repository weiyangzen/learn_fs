# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/acpi.c

Purpose: `acpi.c` is the ACPI front end for AMD HSMP. It binds ACPI HID `AMDI0097`, parses ACPI `_CRS` and `_DSD` mailbox descriptions for each socket, maps the mailbox MMIO region, validates HSMP via the common mailbox test, and exposes misc-device, sysfs, binary metrics, and optional hwmon interfaces.

Important APIs, types, and functions: `struct hsmp_sys_attr` binds a device attribute to an HSMP message ID. `amd_hsmp_acpi_rdwr()` performs MMIO reads/writes. `hsmp_get_uid()` maps ACPI UID strings like `ID00` to socket indices. `hsmp_read_acpi_crs()` maps the mailbox resource; `hsmp_read_acpi_dsd()` validates the HSMP UUID and extracts message ID/argument/response offsets. `init_acpi()` wires a socket, runs `hsmp_test()`, caches protocol version, maps metrics-table DRAM for protocol v6, and creates hwmon sensors. Attribute show helpers call `hsmp_msg_get_nargs()` and decode bandwidth, firmware version, clocks, and frequency-limit source fields.

Control flow: probe gets the shared `hsmp_pdev`, allocates the socket array once using `topology_max_packages()`, initializes the current ACPI device/socket, and registers the common misc device once. Device groups expose per-ACPI-device attributes and `metrics_bin` when protocol version is v6. Remove deregisters the misc device once and clears the probed flag.

State and persistence: the shared `hsmp_plat_device` singleton stores socket array, protocol version, and misc-device state. Each `hsmp_socket` stores MMIO base, offsets, mapped address, semaphore, socket index, and device pointer. No persistent storage exists; sysfs reads trigger live mailbox messages.

Dependencies and integration points: depends on ACPI methods `_CRS`, `_DSD`, device UID naming, common HSMP exported functions, miscdevice, sysfs binary attributes, topology package count, and optional hwmon. It imports the `AMD_HSMP` namespace.

Risks: `_DSD` parsing assumes expected package shape and nonzero offsets, so firmware defects block probing. The shared `proto_ver` is overwritten per socket and assumed uniform. `apmf_notify_smart_pc_update`-style partial initialization is not present, but allocating the socket array under the first ACPI device means devm lifetime is tied to that device while other socket devices may still exist. `hsmp_acpi_remove()` unregisters the misc device on any remove when `is_probed` is true, even in multi-socket scenarios.

Test signals: ACPI resource and UUID validation, per-socket UID parsing, successful `hsmp_test(0xDEADBEEF)`, `/dev/hsmp` misc node, sysfs attribute reads with decoded values, protocol-v6 `metrics_bin`, hwmon power sensors, and clean unload/rebind across multiple socket ACPI devices.
