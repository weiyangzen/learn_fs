<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c

Purpose: preserves the legacy bridge ioctl ABI. It supports old `brctl`-style bridge creation/deletion, bridge listing, port add/delete, bridge and port information queries, STP and timer configuration, path cost and priority changes, and old-format FDB dumps. Newer control-plane features live in rtnetlink, but this file keeps compatibility for `SIOCGIFBR`, `SIOCSIFBR`, `SIOCBRADDBR`, `SIOCBRDELBR`, `SIOCBRADDIF`, `SIOCBRDELIF`, and `SIOCDEVPRIVATE`.

Important APIs, types, and functions:

- `br_ioctl_stub()` handles deviceless bridge ioctls and add/delete-port ioctls under RTNL.
- `br_dev_siocdevprivate()` handles deprecated per-bridge private ioctls.
- `old_deviceless()` implements old global bridge commands such as get version, list bridges, add bridge, and delete bridge.
- Helper functions include `br_dev_read_uargs()`, `get_bridge_ifindices()`, `get_port_ifindices()`, `get_fdb_entries()`, and `add_del_if()`.
- Legacy ABI structures include `struct __bridge_info`, `struct __port_info`, and `struct __fdb_entry` from bridge UAPI headers.

Core control flow:

- `br_dev_read_uargs()` reads 2 to 4 unsigned long arguments from user memory and handles 32-bit compat syscalls by copying `unsigned int` arguments and translating the pointer argument with `compat_ptr()`.
- `br_dev_siocdevprivate()` decodes `BRCTL_*` commands on a bridge netdevice. Add/delete interface calls `add_del_if()`. Information commands snapshot bridge or port STP fields and timer values under RCU and copy to userspace. Set commands require `CAP_NET_ADMIN` in the bridge net namespace, call STP/timer setter functions, and notify either a port link update or bridge device state change on success.
- `get_fdb_entries()` caps the request to one page of `struct __fdb_entry`, allocates a temporary kernel buffer, fills it with `br_fdb_fillbuf()`, and copies only the returned number of records to userspace.
- `old_deviceless()` handles global commands. It lists bridge ifindices by walking netdevices under RCU, and creates/deletes bridge devices after copying an IFNAMSIZ name from userspace.
- `br_ioctl_stub()` performs early capability and ifreq parsing for add/delete-port commands, strips alias suffixes after `:`, takes RTNL, dispatches to global or bridge-specific operations, and releases RTNL.

State and persistence behavior:

- This file does not own long-lived state. It reads bridge, port, timer, and FDB state and mutates bridge topology or STP configuration by delegating to `br_add_bridge()`, `br_del_bridge()`, `br_add_if()`, `br_del_if()`, and STP setter functions.
- It preserves ABI quirks such as page-sized FDB dump limits, port number split into low/high fields, default port-list count of 256, and 32/64-bit compatibility handling.
- All topology-changing ioctl operations are serialized by RTNL or by the callee's expected locking. Information queries use RCU where appropriate.

Dependencies and integration points:

- Depends on net namespace capability checks, user-copy helpers, compat syscall support, rtnetlink locking, bridge STP/timer APIs, bridge lifecycle from `br_if.c`, and FDB export from `br_fdb.c`.
- This is an alternative control plane to rtnetlink. It must not expose features that only rtnetlink can configure, but it must keep old behavior stable.

Risks and edge cases:

- User pointer handling is the main risk. Argument counts, compat translation, copy sizes, IFNAMSIZ termination, and page-sized allocations protect old ABI paths from overflows and bad pointers.
- `args[2] >= 2048` in bridge listing avoids excessive allocation, while FDB dumping clamps to `PAGE_SIZE / sizeof(struct __fdb_entry)`.
- Deviceless add/delete bridge commands operate by name and require the target bridge to be down for deletion through `br_del_bridge()`.
- Setters notify state changes only after successful mutation; missing notification would leave old tools with stale state.
- The interface is deprecated and incomplete compared with rtnetlink, so tests should focus on compatibility, not feature parity.

Test signals:

- Run old `brctl` or ioctl-based tests for addbr, delbr, addif, delif, show bridges, showmacs, showstp, setageing, setfd, sethello, setmaxage, stp on/off, setbridgeprio, setportprio, and setpathcost.
- Exercise 32-bit compat ioctl calls on a 64-bit kernel if available.
- Verify permission failures for unprivileged users and namespace-scoped `CAP_NET_ADMIN`.
- Test bad pointers, too few or too many arguments, negative port counts, oversized bridge-list requests, nonexistent devices, and non-bridge targets.
- Compare old FDB dump output against rtnetlink FDB state for normal dynamic and static entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_ioctl.c -->
