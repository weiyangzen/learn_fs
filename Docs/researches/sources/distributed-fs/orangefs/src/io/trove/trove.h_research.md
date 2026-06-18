## sources/distributed-fs/orangefs/src/io/trove/trove.h

Purpose: Declares the public Trove storage interface used by PVFS2/OrangeFS server and I/O layers to manage collections, dataspaces, byte streams, key/value metadata, and asynchronous operation completion.

Important APIs and definitions: Constants define maximum contexts, default test timeout, iterate start/end, dataspace object kinds, operation flags (`TROVE_SYNC`, `TROVE_ATOMIC`, requested-handle, key overwrite modes, binary key, iterate-remove, directory-entry), export flags, and collection setinfo options. Prototypes cover initialization/finalization, storage and collection lifecycle, context management, bstream I/O, keyval operations, dataspace operations, operation tests, collection extended attributes, getinfo/setinfo, and filesystem config.

Control flow: The header documents Trove's asynchronous pattern: most operations initiate work, return an operation ID, and callers complete it with `trove_dspace_test`, `trove_dspace_testsome`, or `trove_dspace_testcontext`. Some management operations return immediate success using the Trove convention normalized by `trove-mgmt.c`.

State and persistence: No state is stored here, but the API defines handles, collection IDs, contexts, flags, vtags, and hints that flow through to persistent storage backends. Setinfo options configure handle ranges, handle timeout, caches, AIO/direct I/O behavior, sync modes, and concurrency.

Dependencies and integration points: Includes PVFS internals, debug/protocol headers, and `trove-types.h`. Implemented mostly by `trove.c` and `trove-mgmt.c`; DBPF supplies concrete storage methods.

Risks: The interface is broad and version-sensitive, especially around hints, flags, and setinfo options. Error reporting is split between initiation return values and later operation state. `trove_migrate` is declared here but not implemented in the researched files. Callers must understand which operations are synchronous, immediate, or asynchronous.

Test signals: API conformance tests should cover every flag and setinfo option, requested-handle creation, context limits, collection lifecycle, bstream/keyval/dspace operation completion, cancellation, invalid arguments, and compatibility between declarations and method-table implementations.
