# sources/distributed-fs/ceph-client/drivers/net/netdevsim/netdevsim.h

Purpose: central internal header for netdevsim, defining shared constants, private structures, feature state, resource IDs, and cross-file function prototypes.

Important APIs/types/functions: defines `struct netdevsim`, `struct nsim_dev`, `struct nsim_dev_port`, `struct nsim_bus_dev`, IPsec/MACsec/VLAN/ethtool/queue structs, devlink resource enums, and prototypes for device, bus, FIB, BPF, health, hwstats, psample, UDP tunnel, IPsec, MACsec, PSP, and TC integration. It also provides config-dependent inline stubs for optional features.

Control flow: the header does not execute logic directly, but it defines object ownership and module boundaries. `struct nsim_dev` represents the simulated devlink/bus device; `struct nsim_dev_port` binds devlink ports to netdevs; `struct netdevsim` is per-netdev private state; optional feature helpers compile to no-ops when dependencies are disabled.

State and persistence: declares volatile in-kernel state: BPF maps/program lists, devlink health/hwstats, FIB and trap data, UDP port arrays, VF configs, peer RCU pointers, PSP stats, IPsec/MACsec tables, VLAN bitmaps, and debugfs dentries. No persistent format is defined.

Dependencies and integration: includes kernel network headers for devlink, ethtool, UDP tunnels, XDP, MACsec, PTP mock, debugfs, netdevice, and list/bitmap support. It is the contract tying `netdev.c`, `fib.c`, feature modules, and bus/devlink files together.

Risks: this header has broad reach; layout or field ownership changes can affect many modules. Optional stub behavior must match real feature error semantics, such as IPsec tx returning true when XFRM offload is disabled and BPF hooks returning `-EOPNOTSUPP`.

Test signals: build coverage across configs with and without `CONFIG_BPF_SYSCALL`, `CONFIG_XFRM_OFFLOAD`, `CONFIG_MACSEC`, `CONFIG_INET_PSP`, and `CONFIG_PSAMPLE`; compile-time coverage catches prototype/field drift.
