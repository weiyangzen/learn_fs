# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-gio.c

Purpose: SGI GIO bus implementation and IP22 GIO slot probing. It exposes a Linux bus type for GIO devices and discovers graphics or expansion cards by safe bus-error-protected reads.

Important APIs and control flow: bus helpers implement device get/put, register/unregister, driver register/unregister, match, probe, remove, shutdown, sysfs attributes, and MODALIAS uevents. `gio_set_master()` and `ip22_gio_set_64bit()` update MC GIO arbitration flags. `ip22_gio_id()` uses `get_dbe()` on 32/16/8-bit reads to distinguish real IDs from pipelined phantom data. `ip22_check_gio()` detects GR2/GR3, Newport, and ID-table devices, allocates `gio_device`, assigns resource/IRQ, and registers it. `ip22_gio_init()` registers the bus and probes slots by chassis type.

State, persistence, and integration: state includes the global `gio` bus device, registered `gio_device` objects, and MC GIO mode bits. Dependencies include initialized `sgimc`, `hpc3c1`, board type, GIO headers, and exception-safe probing. Risks include direct probing of fragile hardware, manual reference handling, and hard-coded slot resources. Test signals are GIO probe logs, sysfs device attributes, driver autoload by `gio:<id>`, and working Newport/Impact/expansion devices.
