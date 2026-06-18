# sources/distributed-fs/ceph-client/include/net/calipso.h

## Purpose
This header declares CALIPSO support for IPv6 security labels as specified by RFC 5570. It defines DOI mapping constants, the DOI object used by NetLabel, cache sysctls, and config-gated initialization, cleanup, and option validation hooks.

## Important APIs, Types, And Constants
- `CALIPSO_DOI_UNKNOWN`, `CALIPSO_MAP_UNKNOWN`, and `CALIPSO_MAP_PASS` define known DOI/mapping values.
- `struct calipso_doi` stores DOI number, mapping type, refcount, list linkage, and RCU callback state.
- `calipso_cache_enabled` and `calipso_cache_bucketsize` are external sysctl variables.
- With `CONFIG_NETLABEL`, `calipso_init()`, `calipso_exit()`, and `calipso_validate()` are implemented by CALIPSO/NetLabel code.
- Without `CONFIG_NETLABEL`, init succeeds, exit is empty, and validation returns true.

## Control Flow And State
At network label subsystem initialization, `calipso_init()` registers CALIPSO support and cache state; shutdown calls `calipso_exit()`. IPv6 option processing can call `calipso_validate()` with the skb and raw option pointer to check option correctness. DOI objects are refcounted and RCU-freed as policy mappings are added and removed by implementation code.

## State And Persistence Behavior
DOI mappings live in kernel memory, are list-linked, and use `refcount_t` plus RCU for lifetime safety. Cache behavior is controlled by sysctls. The header itself provides no persistence; userspace policy loaders are responsible for installing DOI mappings after boot.

## Dependencies And Integration Points
The header depends on Linux types, RCU/list/net/skbuff infrastructure, NetLabel, request sockets, refcounts, and unaligned access helpers. It integrates with IPv6 option parsing, NetLabel policy management, and security-label enforcement.

## Risks
- The disabled-config validation stub returns true, so callers must rely on build configuration for enforcement expectations.
- CALIPSO options are parsed from packet bytes; implementation must handle alignment, length, and malformed options defensively.
- DOI lifetime requires correct refcount and RCU discipline to avoid stale label-policy references.

## Test Signals
- NetLabel/CALIPSO tests should cover DOI add/remove, validation of well-formed and malformed IPv6 CALIPSO options, cache sysctl behavior, and concurrent policy removal while packets are processed.
- Disabled `CONFIG_NETLABEL` builds should verify init/exit stubs and permissive validation behavior.
