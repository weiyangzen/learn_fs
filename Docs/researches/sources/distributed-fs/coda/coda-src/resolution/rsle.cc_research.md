# sources/distributed-fs/coda/coda-src/resolution/rsle.cc

Purpose: implements `rsle`, the VM-resident spool-list entry that stages a directory resolution log record before it is copied into the recoverable RVM volume log. It also reconstructs remote log entries from dumped `recle` buffers and exposes helpers to extract names, child fids, and vnode types from heterogeneous log-record unions.

Important functions: constructors initialize record metadata and optional index/sequence numbers; `init(int op, va_list)` fills the operation-specific union from varargs for stores, creates, symlinks, links, mkdirs, removes, rmdirs, renames, quota changes, null records, and repair records. `CommitInRVM` ensures a vnode log exists, writes the reserved record slot with `RecovPutRecord`, appends it to the vnode log, and updates log-size histograms. `Abort` deallocates a reserved RVM slot. `InitFromRecleBuf` validates dump stamps, advances the caller buffer pointer, overlays the dumped `recle`, and points `name1`/`name2` into the variable-length payload.

Control flow and persistence: new VM entries own dynamically copied names; parsed remote entries borrow payload memory and must not free names. Commit runs inside an RVM transaction and makes records recoverable; abort releases only the reserved slot. Dependencies include `recle`, `recov_vollog`, `ops`, `srv`, `volume`, `vnode`, and resolution statistics.

Risks and tests: varargs ordering is fragile, borrowed name pointers depend on remote-log buffer lifetime, and rename target handling uses several conditional fields. Test with each opcode round-tripping through spool, dump, parse, print, extraction, commit, and abort paths, including rename-with-target and rmdir subtree records.
