# sources/distributed-fs/ceph-client/io_uring/query.c

Purpose: implements blind and ring registration query support so userspace can discover io_uring opcode, feature, zero-copy receive, and shared-CQ metadata without relying on hard-coded constants.

Important APIs/types/functions: `union io_query_data` bounds all result payloads. `io_query_ops()`, `io_query_zcrx()`, and `io_query_scq()` fill individual result structures. `io_handle_query_entry()` validates/copies a linked query header and result buffer. `io_query()` walks the user-provided linked list.

Control flow: `io_query()` rejects nonzero `nr_args`, zeroes a stack result buffer, then follows `hdr.next_entry` up to `IO_MAX_QUERY_ENTRIES`. Each entry copies the header, clamps the requested size to `IO_MAX_QUERY_SIZE`, validates reserved fields and opcode, copies the input payload, fills the selected result, writes the result data with `copy_struct_to_user()`, writes back the header result/size, and reschedules between entries.

State and persistence: no kernel state is persisted. It only copies capability snapshots to userspace and uses an iteration cap to avoid cycles.

Dependencies/integration: depends on UAPI query structs, io_uring feature/setup/enter/SQE flag constants, `struct io_rings`, `struct io_uring`, and zcrx constants.

Risks/test signals: risks are user pointer faults, linked-list cycles, unsupported op handling, and keeping reported constants current with UAPI additions. Test with undersized/oversized buffers, chained queries, invalid reserved fields, unknown query opcodes, zero-copy query, SCQ query, and signal interruption.
