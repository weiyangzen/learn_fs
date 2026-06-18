<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.cc -->
# sources/distributed-fs/coda/coda-src/resolution/ops.cc

Purpose: core resolution log operation support. It initializes/prints variable log-entry payloads, spools VM `rsle` intention records, copies them to recoverable `recle` records, truncates and purges per-vnode logs, and dumps logs for shipment.

Important APIs/control flow: payload classes (`aclstore`, `ststore`, `newstore`, `create_rle`, `symlink_rle`, `link_rle`, `mkdir_rle`, `rm_rle`, `rmdir_rle`, `rename_rle`, `setquota_rle`) provide `init`/`print`. `CreateRootLog` allocates the first recoverable root log record. `CreateResLog` creates an empty per-vnode log. `SpoolVMLogRecord` filters non-directories and disabled resolution, allocates a volume-log slot, builds an `rsle`, initializes it from varargs, and appends it to a vnode list entry. `SpoolRenameLogRecord` creates source and, for cross-directory renames, target parent records. `TruncateLog`, `PurgeLog`, and `FreeVMIndices` coordinate RVM and VM bitmap cleanup. `DumpLog` serializes tree-shaped logs into a buffer.

State/persistence: works across transient VM `rsle` lists and recoverable RVM `rec_dlist`/`recle` storage. Some functions require active RVM transactions; VM bitmap freeing is intentionally deferred until commit success.

Dependencies/integration: tightly integrated with `recov_vol_log`, vnode/volume structures, `resstats`, version vectors, ACL formatting, and `operations` semantics.

Risks/test signals: varargs spooling is type-fragile. `DumpLog` buffer growth loop assigns `newmaxsize = maxsize * 2` repeatedly, which can fail to grow enough for very large child dumps. `fdopen` in print routines may affect fd buffering ownership. Test log allocation exhaustion, wraparound, recursive child logs, rename with deleted directory target, and truncation transaction rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.cc -->
