# File Research: sources/cow-pools/bcachefs-tools/fs/snapshots/delete.c

Implements asynchronous and recovery-time snapshot deletion. The file documents dead leaf snapshots, redundant interior nodes, `WILL_DELETE`, and `NO_KEYS` states. Runtime deletion removes keys and marks interior nodes `NO_KEYS`; actual interior-node tree surgery is deferred to recovery.

Deletion builds lists of trees being cleaned, leaf IDs, interior IDs with surviving children, and an Eytzinger-searchable delete list. It scans snapshot-aware btrees, deletes keys in dying snapshots, and moves keys from dead interior nodes to surviving children when needed. Version 2 accelerates scanning by using inodes first to target extents/dirents/xattrs.

It marks leaf nodes deleted, updates parent/child and snapshot-tree root pointers, handles old/new deletion formats through incompatible-version negotiation, and removes snapshot accounting. Async entry points run under write refs and expose progress/status, while recovery deletion fixes depths/skiplists before removing `NO_KEYS` interior nodes.
