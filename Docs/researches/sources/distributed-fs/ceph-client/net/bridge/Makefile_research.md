<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Makefile -->
# sources/distributed-fs/ceph-client/net/bridge/Makefile

Purpose: maps bridge Kconfig symbols to the bridge module and its optional object files.

Important APIs, types, and functions: no runtime APIs are declared. `obj-$(CONFIG_BRIDGE) += bridge.o` builds the core bridge module. `bridge-y` includes core forwarding, FDB, STP, netlink, ioctl, device, input, and ARP/ND proxy objects. Feature-specific lines append sysfs, netfilter core, multicast/MDB/EHT, VLAN/MST, switchdev, MRP, and CFM objects. `br_netfilter.o` is a separate object selected by `CONFIG_BRIDGE_NETFILTER`.

Control flow: Kbuild composes `bridge.o` from `bridge-y` plus `bridge-$(CONFIG_...)` fragments. `subst m,y` is used for bridge netfilter and IPv6-related object inclusion so module/built-in combinations include compatible support objects.

State and persistence: none directly. The object composition determines which module init code and global registrations exist at runtime.

Dependencies and integration points: integrates the bridge directory with netfilter subdirectory builds, sysfs, multicast, VLAN, switchdev, MRP, and CFM subsystems. It must stay consistent with Kconfig feature gates and source-level `IS_ENABLED` guards.

Risks: missing an object silently removes feature handlers or leaves unresolved symbols. Incorrect `m` versus `y` handling can break mixed built-in/module bridge netfilter builds. Core object ordering is usually not semantically important but all required init/exit providers must be linked.

Test signals: build coverage for combinations of `CONFIG_BRIDGE`, `CONFIG_SYSFS`, `CONFIG_BRIDGE_NETFILTER`, `CONFIG_IPV6`, `CONFIG_BRIDGE_IGMP_SNOOPING`, `CONFIG_BRIDGE_VLAN_FILTERING`, `CONFIG_NET_SWITCHDEV`, `CONFIG_BRIDGE_MRP`, and `CONFIG_BRIDGE_CFM`, plus module load/unload smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/Makefile -->
