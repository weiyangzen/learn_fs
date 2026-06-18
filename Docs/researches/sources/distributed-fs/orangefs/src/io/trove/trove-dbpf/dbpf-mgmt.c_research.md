# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf-mgmt.c

## Purpose
Implements DBPF management operations for storage spaces and collections. It initializes the DBPF backend, opens and closes storage databases, creates/removes collection directory/database layouts, exposes collection attributes/statfs/configuration knobs, starts optional direct-I/O worker infrastructure, and publishes `dbpf_mgmt_ops` plus `dbpf_mgmt_direct_ops`.

## Important APIs, Types, And Functions
Key functions are `dbpf_initialize`, `dbpf_direct_initialize`, `dbpf_finalize`, `dbpf_storage_create`, `dbpf_storage_remove`, `dbpf_collection_create`, `dbpf_collection_remove`, `dbpf_collection_lookup`, `dbpf_collection_clear`, `dbpf_collection_iterate`, `dbpf_collection_setinfo`, `dbpf_collection_getinfo`, `dbpf_collection_seteattr`, `dbpf_collection_geteattr`, `dbpf_collection_deleattr`, and `dbpf_storage_lookup`. The file also defines PINT event identifiers, `my_storage_p`, direct-I/O manager globals, `dbpf_op_type_to_str`, and a direct-I/O completion callback.

## Control Flow
Initialization defines PINT DBPF event schemas, records `dbpf_pid`, opens the storage attribute and collection databases through `dbpf_storage_lookup`, initializes the bstream open cache, and starts the DBPF service thread. Direct mode layers a PINT manager, worker, context, and queue on top. Collection creation records the collection name/id in `collections.db`, creates data/meta directories, creates collection attribute, dataspace attribute, and keyval databases, writes the DBPF version and last-handle records, creates bstream bucket directories, and creates a stranded-bstream directory. Lookup opens the collection DB handles, checks metadata version compatibility, creates the iterator position cache, registers the collection, and clears stranded bstreams.

## State And Persistence
Persistent layout is rooted at configured data and metadata paths: storage-level `storage_attributes.db` and `collections.db`; per-collection `collection_attributes.db`, `dataspace_attributes.db`, `keyval.db`, `bstreams/<bucket>/<handle>.bstream`, and `stranded-bstreams`. Runtime state includes `my_storage_p`, registered `dbpf_collection` instances, open DB handles, attr-cache configuration, sync high/low watermarks, metadata sync mode, immediate completion mode, and direct-I/O worker parameters.

## Dependencies And Integration Points
Uses DBPF DB wrappers, bstream/open-cache code, op queue/threading, sync coalescing, attr cache, handle management, PINT manager/context APIs, statfs helpers, server configuration, and path macros from `dbpf.h`. It is the management vtable consumed by the TROVE method layer and controls collection options used by keyval, dspace, and bstream operations.

## Risks And Test Signals
Risks include partial cleanup on create/remove failures, path construction/truncation, global single-storage assumptions via `my_storage_p`, version parsing/compatibility drift, direct-I/O teardown state not resetting `directio_threads_started`, collection removal while handles are active, and inconsistent returns (`1`, `0`, negative errors). Tests should create/look up/remove storage and collections, verify on-disk layout and version records, exercise same data/meta path and split data/meta path, validate statfs output, set collection watermarks/cache/immediate-completion options, restart over existing collections, and run direct mode startup/finalize.
