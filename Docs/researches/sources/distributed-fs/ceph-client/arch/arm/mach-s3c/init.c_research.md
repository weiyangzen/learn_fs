# sources/distributed-fs/ceph-client/arch/arm/mach-s3c/init.c

Purpose: common Samsung legacy initialization helpers for CPU table matching and platform-data copying.

Important APIs/types/functions: implements `s3c_init_cpu()`-style CPU table selection and `s3c_set_platdata()` helper used by static platform devices.

Control flow: CPU init scans a table for a matching ID/mask, records the selected CPU, and calls map/init hooks. Platform-data helper allocates and copies caller data into a platform device.

State and persistence: maintains selected CPU initialization state and attaches allocated platform data to devices.

Dependencies and integration points: used by board/SoC init and `devs.c` setters.

Risks: unmatched CPU ID prevents SoC-specific init. Platform-data allocation failures can leave devices with missing configuration.

Test signals: CPU table match logs, map/init hook execution, and platform device data after setters.
