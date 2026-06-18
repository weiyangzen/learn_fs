# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/ehea/Makefile

Purpose: Defines the composite object list for the IBM eHEA Ethernet driver.

Important build entries: `ehea-y = ehea_main.o ehea_phyp.o ehea_qmr.o ehea_ethtool.o` combines the netdev/core, hypervisor-call wrapper, queue/memory-region, and ethtool units into one driver. `obj-$(CONFIG_EHEA) += ehea.o` exposes that composite as built-in or module depending on `CONFIG_EHEA`.

Control flow: kbuild compiles the four source files and links them into `ehea.o`. The module entry/exit symbols live in `ehea_main.o`; the remaining units provide referenced helpers and exported internal interfaces.

State and persistence: No runtime state. Build state follows `.config` and kbuild outputs.

Dependencies and integration: Depends on `CONFIG_EHEA` from the parent Kconfig and on all four source files sharing internal headers `ehea.h`, `ehea_qmr.h`, `ehea_hw.h`, and `ehea_phyp.h`.

Risks: Removing any object from `ehea-y` would break link-time references: `ehea_main.o` needs PHYP wrappers, QMR queue/MR helpers, and ethtool setup; `ehea_qmr.o` needs PHYP calls. The Makefile has no conditional feature splits, so all code must compile on every EHEA-supported configuration.

Test signals: `CONFIG_EHEA=y` vmlinux link, `CONFIG_EHEA=m` module link, modpost symbol checks, and targeted `make M=drivers/net/ethernet/ibm/ehea`.
