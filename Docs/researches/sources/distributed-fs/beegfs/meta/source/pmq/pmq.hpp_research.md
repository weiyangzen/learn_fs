## sources/distributed-fs/beegfs/meta/source/pmq/pmq.hpp

Purpose: public C/C++ API for the PMQ persistent queue. It intentionally hides `PMQ` and `PMQ_Reader` internals and exposes enqueue, sync, persistence-status, stats, and sequential reader operations.

Important APIs and types: `PMQ_Init_Params` carries `basedir_path` and optional `create_size`; `PMQ_Stats` combines `PMQ_Enqueuer_Stats` and `PMQ_Persister_Stats`; `PMQ_Persist_Info` exposes the oldest chunk CSN and next MSNs for chunk store and WAL. `PMQ_Read_Result` provides explicit read outcomes: success, too-small buffer, EOF, out-of-bounds, I/O error, and integrity error. The C++ RAII aliases `PMQ_Handle` and `PMQ_Reader_Handle` wrap the raw handles with `pmq_destroy` and `pmq_reader_destroy`.

Control flow: callers create a queue with `pmq_create`, enqueue using `pmq_enqueue_msg`, make current messages durable using `pmq_sync`, and destroy with `pmq_destroy`, which flushes before cleanup. Readers are created from a queue, positioned with `pmq_reader_seek_to_current`, `pmq_reader_seek_to_oldest`, or `pmq_reader_seek_to_msg`, and advanced with `pmq_read_msg`.

State and persistence behavior: the header documents that a queue directory is either loaded if it exists or created if absent. `pmq_reader_find_old_msn` warns that the oldest persisted message may be discarded concurrently. `pmq_reader_eof` is a cheap synchronization-oriented check based on current persisted cursors, not a blocking wait.

Dependencies and integration points: depends only on fixed-size integer and size headers, keeping the C surface lightweight. The RAII wrapper requires C++ compilation and `std::swap` availability through transitive includes in current use.

Risks: `pmq_enqueue_msg` asserts nonzero size in the implementation, but the public header does not document the zero-size restriction. The returned `PMQ_Persist_Info` is a snapshot and can become stale immediately under concurrent enqueue/persist/discard. Reader positioning semantics require callers to handle `Out_Of_Bounds` and retry after concurrent discard.

Test signals: API-level tests should exercise RAII destruction, failure from invalid/create-size paths, all `PMQ_Read_Result` values, reader EOF behavior before and after sync, and documented stale-snapshot behavior around persistence info.
