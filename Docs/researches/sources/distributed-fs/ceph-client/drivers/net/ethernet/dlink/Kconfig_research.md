<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig

Purpose: Kconfig menu for D-Link Ethernet drivers under `drivers/net/ethernet/dlink`.

Important configuration entries: `NET_VENDOR_DLINK` is a bool vendor gate, defaults to `y`, and depends on `PCI`; disabling it hides the D-Link submenu without directly removing core kernel functionality. `DL2K` is a tristate for DL2000/TC902x/IP1000A Gigabit Ethernet support, depends on `PCI`, selects `CRC32`, and builds module `dl2k`. `SUNDANCE` is a tristate for Sundance Alta chips, depends on `PCI`, selects `CRC32` and `MII`. `SUNDANCE_MMIO` is a bool subordinate to `SUNDANCE` that opts into memory-mapped I/O; help text warns PIO is safer by default for some chips.

Control flow: Kconfig controls compilation symbols consumed by the D-Link Makefile. The `if NET_VENDOR_DLINK` block scopes all device-specific prompts under the vendor gate.

State and persistence: Configuration state persists in the kernel `.config`, not in this source file. The file itself defines dependency and select relationships only.

Dependencies and integration: Integrated with the kernel networking Kconfig tree and the adjacent Makefile. `DL2K` maps to `dl2k.o`; `SUNDANCE` maps to `sundance.o`; selected libraries ensure CRC32 and MII helpers are available.

Risks: `select` forces dependencies on, so those helper symbols must remain valid. Defaulting the vendor gate to `y` exposes prompts broadly. Enabling `SUNDANCE_MMIO` can regress hardware where PIO avoids chip bugs.

Test signals: Kconfig menu visibility with `PCI=n`, module/built-in combinations for `DL2K` and `SUNDANCE`, correct helper symbols selected, and Makefile objects emitted for each tristate value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dlink/Kconfig -->
