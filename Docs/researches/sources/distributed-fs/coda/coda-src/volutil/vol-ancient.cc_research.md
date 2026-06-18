## sources/distributed-fs/coda/coda-src/volutil/vol-ancient.cc

Purpose: `vol-ancient.cc` advances dump version-vector list files by marking a newly generated list as the ancient baseline for future incremental dumps.

Important APIs/types/functions: `S_NewVolMarkAsAncient` accepts a backup volume id, attaches the volume, derives the parent replicated group id through `VRDB.ReverseFind`, and calls `S_VolMarkAsAncient`. `S_VolMarkAsAncient` builds list paths with `getlistfilename` and renames `newlist` to `ancient`.

Control flow: the new-style RPC gets the backup volume, discovers group/parent ids, delegates, then releases the volume. The underlying operation initializes volutil, computes source and destination list filenames, renames atomically at the filesystem level, disconnects, and returns RPC success or failure.

State and persistence behavior: the persistent state is the list file rename, typically used by `vol-dump` to decide what changed since the previous backup. It also attaches/releases volumes but does not mutate volume RVM data.

Dependencies/integration points: integrates with `VGetVolume`, `VPutVolume`, `VRDB`, and `vvlist.h` filename conventions. It is part of the incremental dump workflow: successful `S_VolNewDump` writes `newlist`, and this RPC promotes it after the client accepts the dump.

Risks: if `rename` fails, future incrementals may fall back to full dumps or use stale baselines. There is no explicit cleanup of an existing destination before rename, so platform rename semantics matter. `S_NewVolMarkAsAncient` does not call `VInitVolUtil` before `VGetVolume`; it relies on caller/server context or delegated call behavior. Group id defaults to 0 when no VRDB entry exists.

Test signals: run after successful full and incremental dumps, verify expected `newlist` to `ancient` transition, missing source file failure, existing destination behavior, non-replicated volumes, and replicated VRDB reverse lookup.
