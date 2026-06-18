# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dcdbas.c

Purpose: Dell Systems Management Base driver for SMI command buffers and host-control shutdown actions; also supplies exported SMI helpers for Dell SMBIOS SMM.

Important APIs/types/functions: Exports `dcdbas_smi_alloc()`, `dcdbas_smi_free()`, and `dcdbas_smi_request()`. Sysfs/bin attributes expose `smi_data`, buffer size/address, `smi_request`, and host-control settings. WSMT detection/remapping and `host_control_smi()` implement firmware buffer and shutdown behavior.

Control flow/state/persistence: Early init registers a platform driver/device. Probe checks WSMT, sets a 32-bit DMA coherent mask, creates sysfs, and registers a reboot notifier. SMI requests are serialized by `smi_data_lock` and raised on CPU 0. Host-control actions are consumed during shutdown.

Dependencies/integration: DMA coherent memory, ACPI WSMT, DMI, CMOS/port I/O, reboot notifier, CPU hotplug locking, sysfs, and `dell-smbios-smm.c`.

Risks/test signals: Firmware-facing privileged path with DMA/physical-address constraints. Test WSMT/non-WSMT systems, sysfs buffer resizing and I/O, valid/invalid SMI magic, CPU0 SMI path, host-control reboot notifier, and unload after sysfs activity.
