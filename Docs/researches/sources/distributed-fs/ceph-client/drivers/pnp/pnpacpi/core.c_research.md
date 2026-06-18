<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c

Purpose: ACPI protocol backend for PnP. It enumerates ACPI PNP devices, creates PnP devices, implements ACPI resource get/set/disable, and supports wake/suspend/resume.

Important APIs/types/functions: `ispnpidacpi()` validates seven-character PnP IDs. Protocol callbacks are `pnpacpi_get_resources()`, `pnpacpi_set_resources()`, `pnpacpi_disable_resources()`, and sleep callbacks `pnpacpi_can_wakeup/suspend/resume()`. `pnpacpi_add_device()` converts an ACPI device into `pnp_dev`. `pnpacpi_init()` registers the protocol and walks ACPI namespace.

Control flow: init exits if ACPI or `pnpacpi=off` disabled, registers protocol, walks ACPI devices, and marks `pnp_platform_devices`. Device add skips already-bound, non-`_CRS`, invalid-ID, or not-present devices. It sets capabilities from ACPI methods/status/flags, parses current `_CRS` resources when active, parses `_PRS` options when configurable, adds compatible IDs, clears resources if inactive, and registers the PnP device.

State/persistence: `num` assigns PnP device numbers. Each PnP device stores the `acpi_device` in companion and `dev->data`, active reflects ACPI enabled status, and resource/options mirror `_CRS`/`_PRS`. ACPI power state may be changed to D0/D3 cold during set/disable/suspend/resume.

Dependencies/integration: ACPI core, PnP core, ACPI resource parser, driver PM/wakeup APIs, boot parameter `pnpacpi=`.

Risks: only strict PNP ID format devices are converted. `_SRS` writes are attempted only if method exists, but resource encode limitations can clear `PNP_WRITE` for multi-interrupt descriptors. `WARN_ON_ONCE` repairs `dev->data` if companion diverges.

Test signals: ACPI namespace devices with `_CRS`/`_PRS`/`_SRS`/`_DIS`, inactive devices, compatible ID filtering, wakeup suspend/resume, and `pnpacpi=off` boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/core.c -->
