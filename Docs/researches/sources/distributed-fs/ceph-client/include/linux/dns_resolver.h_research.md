# sources/distributed-fs/ceph-client/include/linux/dns_resolver.h

## Purpose
This header declares the in-kernel DNS resolver upcall API used by network filesystems such as CIFS DFS and AFS. It abstracts hostname and record resolution through key/request-key style infrastructure.

## Important APIs, types, and functions
The only exported function is `dns_query(struct net *net, const char *type, const char *name, size_t namelen, const char *options, char **_result, time64_t *_expiry, bool invalidate)`. It takes a network namespace, record type, name and length, option string, output result buffer, output expiry time, and invalidation flag.

## Control flow, state, and persistence
The header itself has no state. The implementation resolves or invalidates cached resolver entries and returns dynamically managed result data plus an expiry timestamp. The `invalidate` argument makes the call a cache-control operation as well as a query.

## Dependencies and integration points
It includes the UAPI resolver definitions and forward-declares `struct net`. It integrates with network namespaces, request-key/upcall resolver mechanisms, and filesystem referral code.

## Risks and test signals
Risks include result ownership/lifetime mistakes, namespace leakage, stale cache entries, malformed names/options, and timeout/expiry handling. Tests should cover successful lookup, missing records, invalidation, per-netns isolation, and callers freeing result buffers correctly.
