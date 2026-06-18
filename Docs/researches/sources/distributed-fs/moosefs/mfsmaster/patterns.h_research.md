## sources/distributed-fs/moosefs/mfsmaster/patterns.h

Purpose: declares the creation-pattern subsystem interface for matching, administration, replay, metadata persistence, and cleanup.

Important APIs: `patterns_find_matching` returns the operation mask and selected storage/trash/eattr outputs for a filename and credential set. `patterns_add`/`patterns_delete` are live admin operations with changelog side effects. `patterns_mr_add`/`patterns_mr_delete` are metadata-replay variants. `patterns_sclass_delete` removes patterns tied to a storage class. `patterns_list` serializes active patterns. `patterns_store`, `patterns_load`, `patterns_cleanup`, and `patterns_init` handle metadata lifecycle.

Control flow and integration: filesystem creation paths query matching; admin/status paths add/delete/list; metadata save/load uses the `bio` functions; changelog replay uses `mr` variants; storage class deletion calls `patterns_sclass_delete`.

State and persistence behavior: implementation persists the fixed pattern table in the `PATT` metadata section and compiles glob objects at runtime.

Dependencies: exposes `bio` and fixed-width integer types. Error/status codes are returned as MooseFS `MFS_*` values from the implementation.

Risks: callers must provide a 256-byte name buffer and valid gid array/count. Buffer sizing for `patterns_list` should use the NULL-buffer query mode.

Test signals: matching, list serialization, metadata round trip, and live vs replay add/delete behavior.
