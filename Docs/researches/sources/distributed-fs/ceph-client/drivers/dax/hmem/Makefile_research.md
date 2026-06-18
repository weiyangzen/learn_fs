# sources/distributed-fs/ceph-client/drivers/dax/hmem/Makefile

Purpose: kbuild recipe for HMEM DAX resource discovery and device creation.

Important APIs/types/functions: builds `device_hmem.o` from `device.o` for resource collection and `dax_hmem.o` from `hmem.o` for platform-device conversion, with a comment that `device_hmem.o` deliberately precedes `dax_hmem.o`.

Control flow and state: object order supports initcall ordering: soft-reserve resources are collected before the HMEM platform driver consumes them.

Dependencies and integration: tied to `CONFIG_DEV_DAX_HMEM_DEVICES` and `CONFIG_DEV_DAX_HMEM` from DAX Kconfig.

Risks and test signals: object ordering affects discovery races with ACPI HMAT and CXL fallback. Test boot/module initialization ordering and HMEM device creation with and without CXL DAX enabled.
