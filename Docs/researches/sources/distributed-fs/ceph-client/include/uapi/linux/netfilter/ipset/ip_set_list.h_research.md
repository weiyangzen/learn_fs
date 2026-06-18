# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/ipset/ip_set_list.h

## Purpose
Defines list:set ipset type-specific error codes for referenced set management.

## Important APIs, Types, And Functions
Exports `IPSET_ERR_NAME`, `IPSET_ERR_LOOP`, `IPSET_ERR_BEFORE`, `IPSET_ERR_NAMEREF`, `IPSET_ERR_LIST_FULL`, and `IPSET_ERR_REF_EXIST`.

## Control Flow
List set operations add/delete/test referenced sets, optionally before another set, and return these errors for missing names/references, loops, full lists, or absent references.

## State, Persistence, And Dependencies
State persists as ordered references from a list:set to other sets. Depends on `ip_set.h`.

## Integration Points
Used by ipset list type implementation and userspace error messages.

## Risks
Loop prevention is critical to avoid recursive matching. Ordering operations depend on correct `BEFORE`/reference attribute handling.

## Test Signals
Validate add/delete/test references, before/after ordering, loop rejection, missing reference errors, full-list behavior, and reference removal semantics.
