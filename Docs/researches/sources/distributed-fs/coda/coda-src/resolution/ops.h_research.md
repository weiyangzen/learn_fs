<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.h -->
# sources/distributed-fs/coda/coda-src/resolution/ops.h

Purpose: exported operation-log API for the server resolution subsystem.

Important APIs: declares `SpoolVMLogRecord`, `SpoolRenameLogRecord`, `TruncateLog`, `FreeVMIndices`, `PurgeLog`, `PrintLog`, and `DumpLog`. It also exposes cross-module resolution hooks `RecovDirResolve` and `CheckAndPerformRename`.

Dependencies/integration: includes Coda containers, recoverable lists, vnode/volume list types, and resolution utility headers. Transaction annotations (`EXCLUDES_TRANSACTION`, `REQUIRES_TRANSACTION`) document RVM calling requirements and are important for static or human auditing.

State/persistence: this header defines the boundary between operation execution and recoverable resolution logging. Persistent state is in per-volume `recov_vol_log` and per-vnode `rec_dlist`s; transient state is in `dlist`/`vle` operation lists.

Risks/test signals: `SpoolVMLogRecord` uses varargs, so caller prototypes do not enforce payload shape. Any opcode addition must update `rsle`, `recle`, print/dump, and replay logic together. Tests should cover each declared opcode path plus transaction boundary misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/ops.h -->
