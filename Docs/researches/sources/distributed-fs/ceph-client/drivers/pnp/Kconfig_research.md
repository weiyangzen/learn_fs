<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/Kconfig

Purpose: Top-level Plug and Play configuration. It enables the PnP bus layer and includes ISA PnP, PnP BIOS, and ACPI PnP protocol backends.

Important APIs/types/functions: `menuconfig PNP` depends on `HAS_IOMEM` and either ISA or ACPI. `PNP_DEBUG_MESSAGES` controls whether `pnp_dbg()` can emit runtime debug output. The file sources protocol Kconfigs only under `if PNP`.

Control flow/state: no runtime control flow; it gates compilation and debug availability.

Dependencies/integration: connects the core PnP subsystem with protocol-specific directories.

Risks: disabling PNP removes all protocol enumeration; disabling debug compiles out PnP debug paths.

Test signals: configuration matrices with ISA-only, ACPI-only, and debug-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/Kconfig -->
