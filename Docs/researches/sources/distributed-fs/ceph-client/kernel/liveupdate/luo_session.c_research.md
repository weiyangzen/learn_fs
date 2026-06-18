# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_session.c

## Purpose
`luo_session.c` implements named LUO sessions. A session is an anon-inode file descriptor that groups file descriptors to preserve, serializes the group into KHO memory before kexec, deserializes incoming sessions in the new kernel, and lets userspace retrieve preserved files by token.

## Important APIs, Types, and Functions
Internal `struct luo_session_header` tracks session count, list, rwsem, serialized header pointer, serialized array pointer, and active flag. Global `luo_session_global` has incoming and outgoing headers. Session allocation/lifetime helpers are `luo_session_alloc()`, `luo_session_free()`, `luo_session_insert()`, `luo_session_remove()`, `luo_session_getfile()`, and `luo_session_release()`.

Public/session APIs are `luo_session_create()`, `luo_session_retrieve()`, `luo_session_setup_outgoing()`, `luo_session_setup_incoming()`, `luo_session_deserialize()`, and `luo_session_serialize()`. Session fd ioctls are handled by `luo_session_ioctl()` with operations `luo_session_preserve_fd()`, `luo_session_retrieve_fd()`, and `luo_session_finish()`.

## Control Flow
Creating a session allocates a named session, inserts it into the outgoing list after duplicate/capacity checks, and returns an anon-inode file. Releasing an outgoing session before reboot unpreserves all files and removes the session. Retrieving an incoming session finds it by name, rejects repeated retrieval of the same session, returns an anon-inode file, and marks it retrieved.

Session fd ioctls preserve outgoing file descriptors by token, retrieve incoming file descriptors by token, or finish all files. The ioctl path validates command number, reads user struct size, checks minimum size, uses `copy_struct_from_user()`, and responds through `luo_ucmd_respond()`.

Outgoing setup allocates KHO-preserved session header pages and writes a session FDT node containing the physical header pointer. Serialization freezes each outgoing session's file set, writes the session name and file-set serialized metadata, and records the session count. On failure it walks already serialized sessions in reverse, unfreezes their files, and clears names.

Incoming setup reads the session node and header pointer from the LUO FDT. Deserialization is one-shot and caches the first error. It allocates each incoming session, inserts it, deserializes its files, then frees the preserved session header memory with `kho_restore_free()`.

## State and Persistence Behavior
Persistent session state is a KHO-preserved header page plus `struct luo_session_ser` array entries with session names and serialized file-set descriptors. Runtime state is separated into outgoing and incoming lists protected by r/w semaphores, plus per-session mutexes and retrieval flags. Incoming deserialization failures intentionally leak partial state and require reboot recovery.

## Dependencies and Integration Points
It depends on anon inode files, LUO file-set APIs, KHO preserved allocation, libfdt, UAPI liveupdate session ioctls, and core `/dev/liveupdate` create/retrieve paths.

## Risks and Test Signals
Session lookup is linear and duplicate names are rejected with bounded string comparison. Release returns errors if finishing an incoming session fails, which can surprise file-close paths. Serialization rollback uses `list_for_each_entry_continue_reverse()` and must match the already frozen prefix. Tests should cover capacity (`LUO_SESSION_MAX`), duplicate names, outgoing release cleanup, incoming repeated retrieval rejection, session ioctl ABI sizing, serialization failure rollback, one-shot deserialization error caching, and finishing with unretrieved files.
