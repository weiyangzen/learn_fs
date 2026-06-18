# sources/distributed-fs/orangefs/src/io/trove/trove-dbpf/dbpf.h

## Purpose
Central DBPF backend header defining on-disk path conventions, storage/collection structures, keyval database layout, operation union payloads, operation types/states, sync/event/perf macros, and management/bstream/keyval prototypes.

## Important APIs, Types, And Functions
Important definitions include `TROVE_DBPF_VERSION_VALUE`, path macros for storage/collection/databases/bstreams/stranded bstreams, `DBPF_BSTREAM_MAX_NUM_BUCKETS`, `struct dbpf_storage`, `struct dbpf_collection`, `struct dbpf_keyval_db_entry`, key type enum, all operation-specific union structs, `struct dbpf_op`, `enum dbpf_op_type`, `enum dbpf_op_state`, `DBPF_OP_IS_*`, `DBPF_OP_DOES_SYNC`, `struct dbpf_aio_ops`, and DB sync/event/perf macros. It declares DBPF vtables and many management/bstream/keyval helper APIs.

## Control Flow
The header models DBPF's common operation path: API wrappers populate `struct dbpf_op` with a type, handle, collection pointer, service function, user pointer, flags, context id, hints, and type-specific union payload. Queue/thread code later dispatches `svc_fn`, sync macros decide durability work, and event macros instrument the operation.

## State And Persistence
Defines the persistent storage schema: collection records, collection/dataspace/keyval DB names, bstream bucket pathing, stranded-bstream pathing, and keyval composite key format. Runtime collection state includes DB handles, handle ledger, root handle, keyval position cache, sync watermarks/mode, and immediate-completion mode.

## Dependencies And Integration Points
Includes TROVE core types, gen locks, keyval pcache, open-cache, PINT events, and DB wrapper types. It is the shared contract among DBPF bstream, dspace, keyval, context, collection, management, sync, queue, and thread files, plus external TROVE method registration.

## Risks And Test Signals
Risks include ABI/layout drift across many C files, path macro truncation or inconsistent leading slashes, DBPF version compatibility assumptions, fixed max key length mirrored elsewhere, operation enum/string-map drift, and subtle macro side effects. Test signals include full DBPF build, storage upgrade/version checks, path layout verification, operation enum coverage in `dbpf_op_type_to_str`, and integration tests spanning keyval/dspace/bstream operations.
