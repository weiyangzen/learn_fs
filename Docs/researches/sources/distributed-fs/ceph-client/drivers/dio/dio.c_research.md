# sources/distributed-fs/ceph-client/drivers/dio/dio.c

Purpose: scans HP300 DIO/DIO-II address spaces, identifies installed boards, registers them as DIO devices, and provides early select-code lookup helpers.

Important APIs/types/functions: defines global `struct dio_bus dio_bus`, `dio_find()`, `dio_scodetophysaddr()`, and `dio_init()`. It includes a built-in id-to-name table under local `CONFIG_DIO_CONSTANTS`.

Control flow: `dio_find()` is an early console helper that scans select codes, skips holes, maps DIO-II pages when needed, reads primary and optional secondary ids with fault-safe access, and returns the matching select code or `-1`. `dio_init()` runs as `subsys_initcall`, exits unless `MACH_IS_HP300`, registers the DIO bus device, requests DIO memory resource ranges, then scans all select codes. For each present board it allocates `struct dio_dev`, fills bus/device/resource/id/interrupt/name fields, unmaps DIO-II temporary mappings, registers the device, and creates sysfs files.

State and persistence behavior: `dio_bus` holds resource ranges and the bus device. Each discovered `struct dio_dev` persists as a registered device until driver core cleanup; `dio_dev_release()` frees it. There is no dynamic rescan/removal path in this file.

Dependencies and integration points: depends on HP300/m68k machine macros, DIO address/id macros, `copy_from_kernel_nofault()`, `ioremap()`/`iounmap()`, iomem resources, and `dio_bus_type` from `dio-driver.c`. The sysfs helper from `dio-sysfs.c` is called for each device.

Risks and test signals: device allocation failure aborts scanning with `-ENOMEM`, potentially after some devices/resources are registered. Resource requests are not checked for failure. The name table is retained rather than init-discarded. Test signals include boot-time scan logs on HP300, correct select-code physical addresses, sysfs resource ranges, early console `dio_find()` returning known hardware, and graceful no-op on non-HP300 systems.
