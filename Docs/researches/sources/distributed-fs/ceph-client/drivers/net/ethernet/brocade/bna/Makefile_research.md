# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/Makefile

Purpose: kbuild composition file for the BNA network driver module/object.

Important APIs/types/functions: `obj-$(CONFIG_BNA) += bna.o` defines the final built unit. `bna-objs` aggregates `bnad.o`, `bnad_ethtool.o`, `bnad_debugfs.o`, `bna_enet.o`, `bna_tx_rx.o`, `bfa_msgq.o`, `bfa_ioc.o`, `bfa_ioc_ct.o`, `bfa_cee.o`, and `cna_fwimg.o`.

Control flow: kbuild compiles each listed object and links them into `bna.o` when `CONFIG_BNA` is enabled. The object list reflects the driver layering: Linux netdev front end, ethtool/debugfs, Ethernet/TX/RX core, firmware message queue, IOC/hardware-specific IOC, CEE, and embedded firmware image.

State and persistence behavior: no runtime state in this file. Build artifacts persist under the kernel build tree as object files and optionally `bna.ko`.

Dependencies and integration points: integrates with `CONFIG_BNA`, the parent Makefile, and all source files named in `bna-objs`. It also implies that `bfa_ioc.c`, `bfa_cee.c`, and `cna_fwimg.c` are linked into the same module and can share internal symbols.

Risks: object ordering can matter for initialization sections and symbol resolution. Omitting `cna_fwimg.o` would break firmware image lookup, and omitting `bfa_ioc_ct.o` would break ASIC-specific IOC hooks.

Test signals: module link should resolve all `bfa_nw_*`, `bna_*`, and firmware-image symbols; `CONFIG_BNA=m` should produce one `bna.ko`.
