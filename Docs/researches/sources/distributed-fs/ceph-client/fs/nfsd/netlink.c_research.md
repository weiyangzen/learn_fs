# sources/distributed-fs/ceph-client/fs/nfsd/netlink.c

## Purpose
`netlink.c` is generated Generic Netlink glue for NFSD administrative control. It defines attribute validation policies, command operation tables, and the NFSD netlink family registration object.

## Important APIs, types, and functions
The file exports nested policies `nfsd_sock_nl_policy` and `nfsd_version_nl_policy`, defines command-specific policies for thread, version, listener, and pool-mode setters, and builds `nfsd_nl_ops`. The public family is `struct genl_family nfsd_nl_family`.

## Control flow
Generic Netlink dispatch validates incoming attributes using the policy for each set operation, then calls handlers declared in `netlink.h`: RPC status dump, thread set/get, version set/get, listener set/get, and pool mode set/get. Admin-only setters carry `GENL_ADMIN_PERM`; read operations advertise do or dump capabilities. The family is namespace-aware and allows parallel operations.

## State and persistence
The file itself holds static policy/ops tables only. Persistent runtime state is managed by the handler implementations elsewhere in NFSD and by per-net `struct nfsd_net`.

## Dependencies and integration points
It is generated from `Documentation/netlink/specs/nfsd.yaml` and depends on Generic Netlink, UAPI `linux/nfsd_netlink.h`, and NFSD handler functions. It is the structured netlink counterpart to older nfsdfs control files.

## Risks and test signals
Risks include generated code drifting from the YAML spec, too-permissive or too-strict attribute policies, incorrect admin permission flags, parallel operation races in handlers, and ABI incompatibility with userspace YNL clients. Test signals include YNL conformance tests for every command, malformed nested attributes, missing optional attributes, non-admin setter attempts, network namespace isolation, and concurrent setter/getter calls.
