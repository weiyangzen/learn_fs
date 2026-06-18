<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c

Purpose: implements the SMB Witness Service client-side registration and notification handling used for clustered/scale-out SMB shares. It communicates with a userspace witness daemon through generic netlink.

Important APIs and types: `struct cifs_swn_reg` tracks registration id, refcount, network name, share name, notification flags, and tcon. Public functions are `cifs_swn_register()`, `cifs_swn_unregister()`, `cifs_swn_notify()`, `cifs_swn_dump()`, and `cifs_swn_check()`. Global state is `cifs_swnreg_idr` protected by `cifs_swnreg_idr_mutex`.

Control flow: registration lookup extracts server/share from `tcon->tree_name`, reuses an existing matching registration or allocates a new IDR entry, then sends a generic-netlink register message with names, IP, notification flags, and Kerberos or NTLM auth attributes. Notifications look up registration id, dispatch resource-state changes to reconnect signaling, or client-move messages to store a new destination address, unregister/register around it, and signal reconnect. Unregister drops the refcount and sends an unregister message on final release.

State and persistence: registrations live in-memory and are refcounted across tcons sharing the same network/share name. Server `swn_dstaddr` and `use_swn_dstaddr` persist until reset to steer reconnects.

Dependencies and integration: depends on generic netlink family definitions, CIFS netlink attributes, tcon/session/server state, auth selection, reconnect signaling, hostname/share extraction, fscache include side effects, and proc DebugData through `cifs_swn_dump()`.

Risks: auth material, including NTLM passwords, is placed in netlink messages to the daemon. IDR entries are protected by a mutex, but notification lookup releases the mutex before using the registration, so lifetime assumptions depend on external serialization by netlink paths and active mounts. Client-move address handling must preserve port and avoid reconnect loops.

Test signals: register/unregister refcount sharing, missing or invalid netlink attributes, Kerberos and NTLM auth messages, resource unavailable/available notifications, client move to IPv4/IPv6, unregister/register failure during move, echo-task `cifs_swn_check()` retry, DebugData dump, and concurrent unmount while notifications arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c -->
