## sources/distributed-fs/moosefs/mfsmaster/merger.h

Purpose: exposes the small changelog-merging API used by metadata restore.

Important APIs: `merger_start(files, filenames, maxhole, minlv, maxlv)` initializes a heap over changelog files, filters unusable files, and records allowed id gaps and progress boundaries. `merger_loop(verblevel)` applies all changes in sorted order through the restore subsystem and returns restore status.

Control flow and integration: callers initialize once, then run the loop. In this tree, `metadata.c` is the main caller during automatic restore after choosing a metadata snapshot and gathering changelog files.

State and persistence behavior: implementation state is process-global between start and loop. It writes no metadata itself; it drives replay into in-memory metadata through `restore_file`.

Dependencies: only fixed-width integer types are exposed.

Risks: the API is not reentrant because heap state is global. Callers must keep filename strings valid through `merger_start`; the implementation duplicates accepted filenames through `sharedpointer` internally.

Test signals: compile users, then verify restore order and error propagation with controlled changelog inputs.
