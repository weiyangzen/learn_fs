# sources/distributed-fs/ceph-client/drivers/net/Kconfig

Purpose: top-level Kconfig for Linux network device support in this source tree. It defines `NETDEVICES`, the `NET_CORE` submenu, many virtual/core device options, and sources subordinate driver-family Kconfig files, including ARCNET.

Important symbols in scope: `NETDEVICES` depends on `NET`; `NET_CORE` gates core virtual/networking drivers. The requested code is directly tied to `AMT`, which depends on `INET && IP_MULTICAST` and selects `NET_UDP_TUNNEL`, and `NETDEV_LEGACY_INIT`, which depends on `ISA` and enables `Space.o`. `source "drivers/net/arcnet/Kconfig"` pulls in the ARCNET driver family. Other symbols in this file establish neighboring build context for VXLAN, GENEVE, GTP, TUN/TAP, veth, Xen, vmxnet3, and netdevsim.

Control flow and integration: this file has no runtime control flow. It controls whether the Makefile builds `amt.o`, `Space.o`, and the `arcnet/` subdirectory. AMT becomes a module named `amt` and exposes rtnetlink link kind `"amt"` at runtime. `NETDEV_LEGACY_INIT` exists to retain old ISA boot-time probing helpers.

State and persistence: selections persist in `.config`; source inclusions define the configuration tree. Risks include dependency changes that allow build without required network stack pieces, and broad top-level edits causing unrelated driver churn. Test signals are `allmodconfig`, `allyesconfig`, `randconfig` around `AMT`, `ARCNET`, `NETDEV_LEGACY_INIT`, and link-time dependency checks for selected symbols.
