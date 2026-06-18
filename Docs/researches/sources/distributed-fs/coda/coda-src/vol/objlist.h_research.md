# sources/distributed-fs/coda/coda-src/vol/objlist.h

Purpose: declares a C-style object-list structure for per-fid server objects, but it appears stale or incomplete relative to the rest of the C++ volume code.

Important types: `objlist` should contain a list head; `obj` stores a `ViceFid`, `Vnode *`, spool/log lists, and a union of file cleanup state or directory reintegration state. Macros mirror `vlist.h` field aliases (`f_sid`, `d_needsres`, etc.).

Control flow/state: objects are intended to track temporary resources during operations: file store ids and inodes to decrement/truncate on success/failure, or directory cloned inode/log-resolution flags during reintegration. That mirrors `vle` in `vlist.h`.

Dependencies/integration: depends on Coda server, directory, vnode, and list headers. Risks are very high because the header has malformed `extern "C"` closing comments, a missing semicolon after `struct objlist`, type/name mismatch with `objlist.c`, use of `olist` without visible include, and union field named `obj_u` while macros expect `u`. Test signals: whether this header is included in any build target, direct compilation, and migration/removal decisions against the working `vlist` implementation.
