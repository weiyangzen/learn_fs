# sources/distributed-fs/ceph-client/Documentation/netlink/specs/nfsd.yaml

Purpose: specifies the Generic Netlink API for NFSD server configuration and status.

Important APIs/types/functions: protocol is `genetlink`, UAPI header `linux/nfsd_netlink.h`. Attribute sets cover `rpc-status`, `server`, `version`, `server-proto`, `sock`, `server-sock`, and `pool-mode`. `rpc-status` carries pending RPC metadata including xid, flags, program/version/procedure, service time, IPv4/IPv6 source/destination, ports, and compound NFSv4 operations. `server` carries thread counts, grace/leasetime, scope, min threads, and a 16-byte file-handle key. Version and socket sets model enabled protocol versions and listener addresses/transports.

Control flow: `rpc-status-get` dumps pending NFSD RPCs. Administrative setters configure threads/server parameters, enabled protocol versions, listeners, and pool mode. Getters return the corresponding server, version, listener, and pool-mode state. `threads-set`, `version-set`, `listener-set`, and `pool-mode-set` require `admin-perm`; read operations do not.

State and persistence: represented state is the running NFSD service: thread pools, grace and lease timers, server scope, file-handle key, enabled NFS protocol versions, listeners, pool mode, and pending RPCs. Persistence is controlled by NFSD/service configuration outside this YAML; netlink changes affect live kernel server state.

Dependencies and integration points: integrates NFSD kernel code with generated netlink UAPI and userspace NFS administration tools. The schema complements or replaces older procfs/sysfs configuration paths.

Risks: server socket addresses are binary/nested and may contain family-specific layouts not fully described in YAML. Changing listener, version, or pool state while service is active can have client-visible effects. `fh-key` has exact 16-byte validation and is accepted only on set, not returned by get, which is appropriate but requires tools to avoid assuming round-trip visibility. RPC status contains mixed endian network fields.

Test signals: check get/set round trips for threads, versions, listeners, and pool mode; validate exact `fh-key` length; dump pending RPCs under load; verify port/address byte order; and enforce privilege checks on setters.
