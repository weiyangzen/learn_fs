## sources/distributed-fs/moosefs/mfsmaster/openfiles.c

Purpose: tracks which sessions have which inodes open. It supports live client open/release synchronization, metadata serialization of open files, restoration/replay operations, lsof-style reporting, and lock cleanup when a file is closed.

Important APIs and types: `ofrelation` links one `(sessionid, inode)` into both session and inode hash chains using next pointers and pointer-to-previous links. Static hash tables index by session and inode. Public APIs include `of_openfile`, `of_sync`, `of_session_removed`, `of_isfileopen`, `of_isfileopened_by_session`, `of_noofopenedfiles`, `of_lsof`, `of_sessions_info_for_inode`, `of_mr_acquire`, `of_mr_release`, `of_store`, `of_load`, `of_cleanup`, and `of_init`.

Control flow: `of_openfile` inserts a relation if absent and writes an `ACQUIRE` changelog. `of_sync` sorts the provided inode list, removes currently tracked opens not present in the list with `RELEASE` changelogs, and adds missing opens with `ACQUIRE` changelogs. Deleting a node calls `flock_file_closed` and `posix_lock_file_closed` before unlinking from both hashes. Metadata replay APIs mutate state without changelogging and increment metadata version. Load reads fixed 8-byte records until a zero/zero terminator, only restoring entries whose sessions still exist.

State and persistence behavior: open file relations are persisted in the `OPEN` metadata section version `0x10`. Live user operations are changelogged, and replay operations increment metadata version. Cleanup frees all relation nodes and clears hash heads.

Dependencies and integration points: depends on `metadata`, `flocklocks`, `posixlocks`, `sessions`, `changelog`, `main`, `datapack`, `bio`, and MooseFS status codes. `metadata.c` stores/loads the section and orders locks after open files because lock cleanup depends on open state.

Risks: `of_sync` mutates and sorts the caller-provided inode array. The static bitmask cache grows but only frees on process exit. Duplicate prevention depends on checking before insert for live paths; replay/load paths assume input consistency. Lock cleanup is coupled to every delete path through `of_delnode`.

Test signals: test acquire/release changelog emission, sync add/remove/no-op behavior, session removal lock cleanup, metadata store/load with missing sessions, lsof sizes/data for all vs one session, replay mismatch errors, and duplicate open prevention.
