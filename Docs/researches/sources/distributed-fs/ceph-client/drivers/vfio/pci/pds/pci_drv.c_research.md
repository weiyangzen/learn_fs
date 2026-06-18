# sources/distributed-fs/ceph-client/drivers/vfio/pci/pds/pci_drv.c

Purpose: registers the AMD/Pensando PDS VFIO PCI driver and handles PF-client registration and recovery notifications.

Important APIs and functions: `pds_vfio_pci_probe()`, `pds_vfio_pci_remove()`, PDS event notifier registration, reset/recovery handling, AER reset handler, and PCI driver table matching Pensando Ethernet VF override IDs.

Control flow: probe allocates the VFIO device, registers it with VFIO PCI core, registers as a PDS client, and subscribes to PDS reset notifications. On reset-complete notifications, if migration or dirty tracking is active, it moves the VFIO migration state to ERROR because kernel migration drivers must not asynchronously transition to a normal state outside user/VFIO reset control. Remove unregisters notifier, client, VFIO core device, and device reference.

State and persistence: stores notifier callback in `pds_vfio->nb` and the firmware client id through `cmds.c`. Recovery updates in-memory VFIO state and releases migration/dirty resources through `pds_vfio_reset()`.

Dependencies and integration: depends on PDS core notify APIs, VFIO allocation/register helpers, PDS command registration, and `vfio_dev.c` device ops.

Risks: notifier lifetime must be torn down before device release. Recovery must not silently resume migration after PF reset, or userspace could believe stale device state is valid. Probe unwinding must unregister in reverse order.

Test signals: probe failure at each stage, client unregister on remove, PDS reset notification while running, while stop-copy/resuming, and while dirty logging is enabled, plus AER reset-done path.
