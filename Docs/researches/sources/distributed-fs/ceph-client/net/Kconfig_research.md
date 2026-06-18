# sources/distributed-fs/ceph-client/net/Kconfig

Purpose: top-level kernel networking Kconfig menu. It declares the primary `NET` option, core hidden feature flags, user-visible networking options, protocol family includes, testing options, and shared helper symbols consumed by drivers and subsystems.

Important APIs, types, and functions: this is Kconfig, so key entities are symbols rather than C APIs. Major symbols include `NET`, `COMPAT_NETLINK_MESSAGES`, `NET_INGRESS`, `NET_EGRESS`, `NET_XGRESS`, `NET_DEVMEM`, `NET_SHAPER`, `NET_CRC32C`, `NET_HANDSHAKE`, `INET`, `NETFILTER`, `BRIDGE_NETFILTER`, `MAX_SKB_FRAGS`, `RPS`, `XPS`, `CGROUP_NET_PRIO`, `CGROUP_NET_CLASSID`, `NET_PKTGEN`, `NET_DROP_MONITOR`, `WIRELESS`, `LWTUNNEL`, `PAGE_POOL`, `FAILOVER`, `ETHTOOL_NETLINK`, and KUnit-related test symbols.

Control flow: Kconfig evaluation starts at `menuconfig NET`; all nested options are active only under `if NET`. The file includes many subsystem Kconfig files in a fixed order, including `net/atm/Kconfig`, `net/appletalk/Kconfig`, `net/9p/Kconfig`, and `net/ceph/Kconfig`. Some features select lower-level dependencies, such as `NET` selecting `NLATTR`, `GENERIC_NET_UTILS`, and `BPF`; `NET_XGRESS` selecting ingress/egress; and `NET_CRC32C` selecting `CRC32`.

State and persistence: configuration state persists in the kernel `.config` and controls compile-time object inclusion and built-in/module choices. There is no runtime state in this file.

Dependencies and integration points: integrates every networking subtree into the kernel build configuration. It gates the Makefile entries researched in this subset and exposes options that alter runtime behavior across net/core, protocol families, offloads, tests, and driver helpers.

Risks: ordering matters for menu organization and dependency visibility; missing `source` entries silently hide subsystems. Incorrect `select` usage can force dependencies without their prerequisites. Compatibility symbols are explicitly discouraged for new code. `MAX_SKB_FRAGS` range changes can expose legacy driver bugs.

Test signals: `make olddefconfig`, `allyesconfig`, `allmodconfig`, and targeted configs with `NET=n`, `INET=n`, `ATLK/ATM/NET_9P` toggles. Kconfig warnings, unmet dependency reports, and expected object inclusion from `.config` are the primary validation outputs.
