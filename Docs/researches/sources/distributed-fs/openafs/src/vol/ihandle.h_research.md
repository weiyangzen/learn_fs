# sources/distributed-fs/openafs/src/vol/ihandle.h

Purpose: public abstraction layer for OpenAFS inode/file handling. It hides whether the backing store is traditional inode syscalls, NAMEI files, or NT file handles, and exposes inode handles, descriptor handles, stream handles, cache parameters, lock macros, and portable OS operation macros.

Important APIs/types/functions: `IHandle_t` identifies a stored object by volume id, device, inode, flags, sync state, refcount, and descriptor list. `FdHandle_t` wraps a real fd/HANDLE with status, refcount, parent handle, LRU/free links, and per-ihandle links. `StreamHandle_t` implements simple buffered positioned I/O. Status constants include `FD_HANDLE_AVAIL`, `OPEN`, `INUSE`, and `CLOSING`; stream directions; `IH_SYNC_ALWAYS`, `IH_SYNC_ONCLOSE`, and `IH_SYNC_NEVER`; cache sizing defaults; and `IH_REALLY_CLOSED`. The header declares lifecycle functions and maps public macros such as `IH_INIT`, `IH_OPEN`, `FDH_CLOSE`, `FDH_SYNC`, `FDH_PREAD`, `IH_CREATE`, `IH_INC`, and `IH_DEC` to implementation or platform-specific backends.

Control flow: callers generally allocate/acquire an `IHandle_t`, open it to an `FdHandle_t`, use `FDH_*` operations, then close or really close descriptor handles and release the inode handle. The macros intentionally mutate pointer variables for close/release paths to reduce stale pointer use.

State and persistence: the header defines state layout but not storage. Runtime state is managed by `ihandle.c`. Persistent behavior is backend-dependent: NAMEI paths create/read/write ordinary files and link-count metadata; traditional inode paths invoke inode syscalls; NT paths map to Win32 handle operations.

Dependencies: pthread and OpenAFS lock wrappers, AFSSYSCALLS, NAMEI/NT headers when selected, filesystem large-file feature macros, stat/statfs variants, and platform lock/unlink/path separator APIs.

Integration points: this is a central include for volume, vnode, salvage, list-inodes, and utility code. It also documents an important contract: `IH_REALLYCLOSE` is not safe to race with `IH_OPEN` on the same handle.

Risks: heavy macro indirection makes behavior build-configuration-sensitive. Some macro close/release forms evaluate and null the argument, so callers must pass lvalues. The fixed hash function depends on `IHandle_t` layout assumptions used by the dir package. Cache-size defaults reflect old stdio fd limitations and must be tuned carefully. Platform branches can drift because many are rarely built.

Test signals: compile matrix for NAMEI, non-NAMEI, NT, large-file, positional-I/O, and vector-I/O configurations; macro expansion/link tests for all declared operations; cache parameter defaults; path separator behavior; lock macros under pthread and non-pthread builds; and structure-size/layout assumptions used by dependent code.
