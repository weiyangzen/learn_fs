## sources/distributed-fs/moosefs/mfsmaster/openfiles.h

Purpose: declares the open-file relation subsystem used by sessions, metadata, lock managers, status handlers, and changelog replay.

Important APIs: live operations (`of_openfile`, `of_sync`, `of_session_removed`), queries (`of_checknode`, `of_isfileopen`, `of_isfileopened_by_session`, `of_noofopenedfiles`, `of_lsof`, `of_sessions_info_for_inode`), replay operations (`of_mr_acquire`, `of_mr_release`), and metadata lifecycle (`of_store`, `of_load`, `of_cleanup`, `of_init`).

Control flow and integration: session/client code records opens; session teardown removes all opens; lock subsystems are notified indirectly on close; metadata stores and restores the `OPEN` section; changelog replay uses `of_mr_*`.

State and persistence behavior: implementation persists open relations through `bio` and updates metadata version during replay mutations.

Dependencies: exposes `bio` in the store/load API and fixed-width integer types.

Risks: callers of `of_sync` should treat the inode array as scratch because it is sorted in place. Buffer sizing for `of_lsof` and `of_sessions_info_for_inode` must use the size-return mode before writing.

Test signals: API-level tests for open tracking, buffer sizes, metadata round trips, and replay mismatch return codes.
