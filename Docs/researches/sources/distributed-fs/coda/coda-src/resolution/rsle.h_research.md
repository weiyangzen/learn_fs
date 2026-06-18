# sources/distributed-fs/coda/coda-src/resolution/rsle.h

Purpose: declares the `rsle` VM spool-log record class used by RVM-backed directory resolution. The name means RVM spool-list entry, differentiating it from older VM-only resolution log entries.

Important APIs/types: `rsle` inherits `olink` so records can be held in Coda `olist`s. It stores an RVM log index, sequence number, `ViceStoreId`, parent directory vnode/unique pair, opcode, and a union of operation-specific record types from `ops.h` and `recle.h`. Large or variable-length names are kept as `name1` and `name2`, with `namesalloced` controlling destructor ownership. Methods include varargs initialization, RVM commit/abort, reconstruction from a dumped recoverable record buffer, and debug printing to `stdout`, `FILE *`, or fd.

Control flow and integration: producers create or initialize `rsle` instances during normal operation spooling and subordinate resolution. Coordinator/subordinate log parsing uses `InitFromRecleBuf` and then `ExtractVNTypeFromrsle`, `ExtractChildFidFromrsle`, and `ExtractNameFromrsle` to drive semantic checks.

State/persistence: the object itself is VM state; `CommitInRVM` persists into the volume log. Risks are manual ownership of names, varargs type mismatches, and union field interpretation by opcode. Test signals include clean destructor behavior for allocated names, no double-free for parsed names, and correct extraction for all supported opcodes.
