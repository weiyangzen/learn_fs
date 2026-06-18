# sources/distributed-fs/orangefs/src/common/misc/mkspace.h

Purpose: Declares the public interface for creating and removing OrangeFS/TROVE storage spaces and collections. It is a small server/tooling header that exposes the two implementation functions in `mkspace.c` and the verbosity selectors used by callers.

Important APIs and types: `PVFS2_MKSPACE_GOSSIP_VERBOSE` selects gossip debug output, while `PVFS2_MKSPACE_STDERR_VERBOSE` selects direct stderr output. `pvfs2_mkspace()` accepts storage paths, collection name and id, root handle, metadata/data handle range strings, a collection-only mode flag, and a verbosity mode. `pvfs2_rmspace()` accepts the same storage identity and collection id plus a removal-only flag.

Control flow and integration: The header itself has no control flow; it supplies the provisioning contract to utilities and server code that need to manipulate storage spaces. It includes `pvfs2-internal.h` and `trove.h`, so callers see the `TROVE_coll_id` and `TROVE_handle` types required by the function signatures.

State and persistence behavior: The declarations describe functions that mutate persistent DBPF/TROVE storage and collections, but the header owns no state. The collection-only and remove-collection-only flags are key semantic controls for whether the storage directories themselves are created or removed.

Dependencies and risks: Because this header exposes destructive filesystem provisioning operations, callers must pass validated paths, collection ids, and range strings. ABI or signature changes affect server utilities that compile against `mkspace.h`. Test signals are compile coverage for all callers and runtime coverage of both full-space and collection-only modes.
