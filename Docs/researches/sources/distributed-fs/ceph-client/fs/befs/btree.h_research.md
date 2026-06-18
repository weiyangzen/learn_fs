# sources/distributed-fs/ceph-client/fs/befs/btree.h

Purpose: declares the BeFS B+tree lookup and sequential-read interfaces used by the VFS directory layer.

Important APIs/types/functions: `befs_btree_find()` maps a string key to a BeFS value/offset; `befs_btree_read()` returns the key/value at an ordinal position.

Control flow: `linuxvfs.c` calls `befs_btree_find()` during lookup and `befs_btree_read()` during readdir; implementation lives in `btree.c`.

State and persistence: no state in the header; arguments expose datastream-backed persistent B+tree data and caller-owned output buffers.

Dependencies and integration: requires BeFS datastream and offset types from `befs.h`.

Risks: callers must provide adequate key buffers and handle BeFS return codes distinctly from Linux errno values.

Test signals: compile coverage for declarations and directory lookup/readdir behavior.
