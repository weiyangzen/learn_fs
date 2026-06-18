# sources/distributed-fs/ceph-client/Documentation/netlink/specs/lockd.yaml

Purpose: specifies a small Generic Netlink API for configuring the kernel NFS lock manager daemon (`lockd`).

Important APIs/types/functions: family name is `lockd`, protocol `genetlink`, UAPI header `linux/lockd_netlink.h`. The single `server` attribute set has `gracetime`, `tcp-port`, and `udp-port`.

Control flow: `server-set` is an administrative do operation that updates lockd server parameters. `server-get` returns the current parameters. There are no dump or notification operations because the API addresses singleton server configuration.

State and persistence: the YAML is static; the represented state is kernel lockd server configuration. Set values affect the running server and may not persist beyond module unload, reboot, or higher-level service reconfiguration.

Dependencies and integration points: integrates NFS lockd server code with Generic Netlink and generated UAPI definitions. NFS administration tools can use it instead of procfs/sysfs-style configuration.

Risks: singleton configuration means concurrent administrators can race. Port numbers are `u16` and no min/max policy beyond type is expressed. Changing ports or grace time on a running server may have operational effects outside the schema.

Test signals: validate get defaults, set/get round trips, privilege enforcement for `server-set`, boundary ports, and behavior while lockd is active.
