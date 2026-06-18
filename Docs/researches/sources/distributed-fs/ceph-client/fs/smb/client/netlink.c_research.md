# sources/distributed-fs/ceph-client/fs/smb/client/netlink.c

## Purpose
`netlink.c` registers the CIFS generic netlink family used for server witness notification (SWN) integration. It defines accepted attributes, the command dispatcher, multicast groups, and module init/exit hooks for netlink registration.

## Important APIs, types, and functions
The core object is the global `struct genl_family cifs_genl_family`. `cifs_genl_policy` validates attributes such as registration id, network/share/resource names, IP sockaddr storage, notification flags, Kerberos auth flag, username/password/domain, notification type, and resource state. `cifs_genl_ops` maps `CIFS_GENL_CMD_SWN_NOTIFY` to `cifs_swn_notify()`. `cifs_genl_mcgrps` defines the SWN multicast group. Exported lifecycle functions are `cifs_genl_init()` and `cifs_genl_exit()`.

## Control flow
Module initialization calls `genl_register_family()`, logs on failure, and returns the kernel error code. Exit calls `genl_unregister_family()` and logs failures. At runtime, generic netlink validates incoming SWN notify messages against the policy and invokes `cifs_swn_notify()`.

## State and persistence behavior
The persistent local state is generic netlink registration in the kernel and multicast group membership managed by netlink. The file itself stores no per-message state. SWN registration state is maintained by the witness subsystem reached through `cifs_swn_notify()`.

## Dependencies and integration points
It depends on `<net/genetlink.h>`, UAPI definitions in `uapi/linux/cifs/cifs_netlink.h`, `cifs_swn.h`, and CIFS debug logging. It integrates with module load/unload and the witness notification subsystem.

## Risks
Risks are ABI compatibility of policy definitions, accepting unvalidated or underspecified string lengths due to non-strict validation flags, correct sockaddr length handling, registration failure on module init, and multicast group naming/version mismatch with userspace witness clients.

## Test signals
Test family registration/unregistration, duplicate registration failure paths, malformed SWN messages, missing required attributes as interpreted by `cifs_swn_notify()`, oversized strings, invalid sockaddr lengths, multicast group discovery from userspace, and notify behavior across module unload.
