## sources/distributed-fs/beegfs/meta/source/session/SessionStore.h

Purpose: declares the top-level client session store and embeds the `EntryLockStore` used to serialize mirrored metadata operations.

Important APIs/types: `SessionReferencer` is `ObjectReferencer<Session*>`; `SessionMap` maps `NumNodeID` to referencers. Public APIs handle session reference/release, synchronization with management node lists, listing IDs, size, serialization/deserialization, file load/save, clear, entry-lock-store access, and equality.

Control flow: callers reference sessions by client node ID and must release them. `getEntryLockStore` exposes the embedded lock store to mirrored message handlers. Private helpers add/remove sessions and relink inodes after deserialization.

State and persistence behavior: `sessions` is process-local but serializable through `SessionStore.cpp`. `entryLockStore` is not persisted; it is runtime synchronization state only. `relinkInodes` removes sessions that become empty after failed file relinks.

Dependencies and integration points: depends on `Node`, `ObjectReferencer`, `Mutex`, `EntryLockStore`, and `Session`. `App` owns normal and mirrored instances of this class.

Risks: raw `Session*` returned from `referenceSession` requires strict release discipline. `relinkInodes` erases map entries without deleting referencers in the shown code path, which should be reviewed in context for ownership leaks if relink failure occurs.

Test signals: reference/release discipline, relink failure removal, entry-lock-store access by mirrored messages, equality, and load/save behavior through the implementation.
