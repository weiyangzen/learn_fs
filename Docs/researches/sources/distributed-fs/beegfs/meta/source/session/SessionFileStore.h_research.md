## sources/distributed-fs/beegfs/meta/source/session/SessionFileStore.h

Purpose: declares the per-session open-file store, its ownership model, serialization format, and recovery helpers.

Important APIs/types: `SessionFileReferencer` is `ObjectReferencer<SessionFile*>`; `SessionFileMap` maps file-handle IDs to referencers. Public APIs include add, recovery add-and-reference, reference, release, remove, remove-all, delete-all, merge, size, relink, serialize/deserialize, and equality.

Control flow: header serialization writes `lastSessionID`, map size, each key, and each `SessionFile`. Deserialization reads those fields, allocates `SessionFile` objects, inserts referencers, and cleans up the current object on per-element failure. `relinkInodes` iterates session files and erases those whose `SessionFile::relinkInode` fails.

State and persistence behavior: `lastSessionID` and all `SessionFile` records are persisted as part of `Session`. Live reference counts are not serialized. Constructor randomizes `lastSessionID`.

Dependencies and integration points: friends `SessionStore` so session-store serialization can inspect nested maps for lock-state persistence. Depends on `MetaStore` through relink declarations, `Random`, `Mutex`, and `ObjectReferencer`.

Risks: `getSessionMap` exposes the internal map to friend/merge code. Deserialization inserts without duplicate checks inside the same serialized stream. Relink erases bad files but leaves the overall result false for caller logging/removal decisions.

Test signals: malformed deserialization cleanup, duplicate serialized keys, relink erasure, `lastSessionID` preservation, and serialization ordering stability.
