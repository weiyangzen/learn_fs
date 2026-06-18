# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-collection.c

## Purpose
`dbpf-collection.c` maintains the process-local registry of opened DBPF collections by collection id. Other DBPF modules use this registry to resolve a `TROVE_coll_id` into the active `struct dbpf_collection`.

## Important APIs, types, and functions
`dbpf_collection_register()` appends a collection to the global list. `dbpf_collection_find_registered()` performs a linear search by `coll_id`. `dbpf_collection_deregister()` removes a registered entry from the list.

## Control flow and state
The only state is `static struct dbpf_collection *root_coll_p`. Registration appends at tail. Lookup walks `next_p` until a matching `coll_id` or `NULL`. Deregistration special-cases the root entry and otherwise relinks the predecessor.

## Persistence and integration
The registry is volatile and does not persist collection metadata. It is a central integration point for bstream, dspace, and keyval entry points, which generally return `-TROVE_EINVAL` when lookup fails.

## Dependencies
It depends on DBPF collection layout from `dbpf.h` and Trove collection ids.

## Risks and test signals
There is no locking in this file, so collection lifecycle must be serialized externally. `dbpf_collection_deregister()` sets `root_coll_p = NULL` when removing the root even if the root has successors, which drops the rest of the list. Tests should cover registering multiple collections, removing head/middle/tail entries, lookup after deregistration, duplicate registration behavior, and concurrent lifecycle assumptions.
