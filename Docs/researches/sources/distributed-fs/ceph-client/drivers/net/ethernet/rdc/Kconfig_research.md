# sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Kconfig

Purpose: Defines kernel configuration entries for RDC Ethernet drivers.

Important entries: `NET_VENDOR_RDC` is a vendor menu gate, defaulting to yes and depending on PCI. `R6040` is a tristate driver option for RDC R6040 Fast Ethernet MACs, depends on PCI, and selects CRC32, MII, and PHYLIB.

Control flow and integration: The Kconfig symbol `CONFIG_R6040` controls compilation in the sibling Makefile. Dependency selection ensures the r6040 driver has CRC hashing, legacy MII helpers, and PHY library support available.

State and persistence: No runtime state. Configuration persists in the kernel build config and determines whether `r6040.o` is built in, modular, or omitted.

Risks and test signals: Risks are missing dependencies if driver code gains new subsystem use, or accidental visibility without PCI. Test signals include allmodconfig/build coverage and verifying `CONFIG_R6040=m` produces module `r6040`.
