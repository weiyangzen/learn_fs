# sources/distributed-fs/ceph-client/drivers/bus/mhi/Kconfig

Purpose: top-level Kconfig include file for the MHI bus subsystem. It does not declare symbols directly; it sources host and endpoint Kconfig files so both halves appear under the MHI bus menu.

Important declarations: it includes `drivers/bus/mhi/host/Kconfig` and `drivers/bus/mhi/ep/Kconfig`.

Control flow and state: configuration-time only. It affects which objects are compiled by making host and endpoint symbols visible to Kconfig.

Dependencies and integration: integrates the MHI host stack (`CONFIG_MHI_BUS`, debugfs, PCI generic controller) and endpoint stack (`CONFIG_MHI_BUS_EP`) into the kernel configuration hierarchy.

Risks and tests: risk is low but path correctness matters; stale source paths would make menuconfig fail. Test signals are `make menuconfig`, `make olddefconfig`, and builds with host-only, endpoint-only, both, and neither enabled.
