<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig

Purpose: Build configuration for ACPI-backed PnP enumeration.

Important APIs/types/functions: `PNPACPI` bool defaults to `PNP && ACPI`.

Control flow/state: build-time only.

Dependencies/integration: enables the ACPI protocol backend when PnP and ACPI are present.

Risks: ACPI PnP disables PnP BIOS at runtime, so configuration affects platform device discovery path.

Test signals: ACPI PnP enabled by default in PNP+ACPI configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/pnpacpi/Kconfig -->
