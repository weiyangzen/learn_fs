# sources/distributed-fs/ceph-client/drivers/nvme/Kconfig

Purpose: Defines the top-level NVMe Kconfig menu and includes the common, host, and target NVMe configuration trees.

Important APIs and flow: The file opens `menu "NVME Support"`, sources `drivers/nvme/common/Kconfig`, `drivers/nvme/host/Kconfig`, and `drivers/nvme/target/Kconfig`, then closes the menu.

State and persistence behavior: No runtime or persistent state. It controls which NVMe subsystems can be configured into the kernel.

Dependencies and integration points: Integrates the common auth/keyring options, host drivers, and target drivers into one visible menu.

Risks and test signals: Build coverage should ensure sourced paths stay valid after tree moves and that host/target/common options appear under the expected menu.
