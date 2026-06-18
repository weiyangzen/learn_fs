# sources/distributed-fs/ceph-client/fs/nfsd/netlink.h

## Purpose
`netlink.h` is the generated header for the NFSD Generic Netlink family. It publishes policies, handler prototypes, and the family object to the rest of the NFSD module.

## Important APIs, types, and functions
It declares `nfsd_sock_nl_policy`, `nfsd_version_nl_policy`, handler prototypes for RPC status dump and all server thread/version/listener/pool-mode get/set commands, and `extern struct genl_family nfsd_nl_family`.

## Control flow
There is no executable flow. Including code registers `nfsd_nl_family`, while the generated ops table in `netlink.c` calls the handler prototypes declared here.

## State and persistence
The header has no state. It describes static netlink family wiring and delegates all mutable server state to handler implementations.

## Dependencies and integration points
It depends on Generic Netlink kernel headers and the NFSD netlink UAPI. Because it is generated from YAML, its contract is shared with userspace YNL tooling.

## Risks and test signals
Risks include manual edits being overwritten or diverging from generated `netlink.c`, prototype mismatches with handler implementations, and UAPI/spec drift. Test signals include regeneration from the YAML spec, build coverage for every declared handler, and userspace netlink ABI tests.
