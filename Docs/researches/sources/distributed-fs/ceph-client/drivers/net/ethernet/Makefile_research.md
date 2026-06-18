# sources/distributed-fs/ceph-client/drivers/net/ethernet/Makefile

Purpose: this top-level Ethernet Makefile maps Kconfig vendor and driver symbols to subdirectories or standalone objects under `drivers/net/ethernet`.

Important APIs, types, and functions: this is Kbuild syntax. Most lines use `obj-$(CONFIG_NET_VENDOR_*) += <vendor>/` to descend into vendor subdirectories. Direct object mappings include `ec_bhf.o` for `CONFIG_CX_ECAT`, `jme.o`, `korina.o`, `lantiq_etop.o`, `lantiq_xrx200.o`, `fealnx.o`, `ethoc.o`, and `oa_tc6.o`. Requested integration points include `obj-$(CONFIG_NET_VENDOR_8390) += 8390/`, `obj-$(CONFIG_NET_VENDOR_ACTIONS) += actions/`, and `obj-$(CONFIG_NET_VENDOR_ADAPTEC) += adaptec/`.

Control flow: during Kbuild, enabled or modular config symbols expand `obj-y` or `obj-m` entries. Vendor directory entries cause recursive descent into the corresponding subdirectory Makefile, where individual driver objects are selected. Disabled symbols expand to nothing and skip both directory traversal and compilation.

State and persistence: there is no runtime state. Build state is determined by `.config`, generated Kbuild variables, and object outputs in the build directory. The file is part of the build graph and persists as source.

Dependencies and integration points: depends on Kbuild semantics and symbol names declared in the top-level and vendor Kconfig files. It must stay synchronized with directory names and config symbols. It integrates with module naming through subdirectory Makefiles that map `CONFIG_*` to `.o` files.

Risks: a config symbol mismatch silently prevents a driver directory or object from building. Adding a vendor Kconfig without a matching Makefile line, or vice versa, creates visible config with no build output or unreachable build rules. Some directories are gated by driver-specific symbols rather than vendor symbols, so consistency checks need to account for both styles.

Test signals: use `make drivers/net/ethernet/` or targeted builds with relevant configs enabled. Confirm `CONFIG_NET_VENDOR_ACTIONS=m` descends into `actions/` and builds `owl-emac.o`, `CONFIG_NET_VENDOR_ADAPTEC=m` descends into `adaptec/`, and `CONFIG_NET_VENDOR_8390` descends into `8390/`. `allmodconfig` should not show missing-directory or unused-object errors.
