## sources/distributed-fs/coda/coda-src/volutil/vol-dumpvrdb.cc

Purpose: `vol-dumpvrdb.cc` dumps the in-memory Volume Replication Database to a text file in the format expected by VRDB rebuild tools.

Important APIs/types/functions: the sole RPC is `S_VolDumpVRDB`, which accepts an output filename, opens it with `O_CREAT | O_EXCL | O_WRONLY`, calls `DumpVRDB(fd)`, closes the descriptor, and returns `0` or `VFAIL`.

Control flow: validate by attempting exclusive file creation, delegate all formatting to `DumpVRDB`, clean up the descriptor, and map any open/dump error to volutil failure.

State and persistence behavior: writes a caller-specified filesystem path. It does not mutate VRDB or volume state. Exclusive creation prevents overwriting existing files.

Dependencies/integration points: depends on `vrdb.h`, `DumpVRDB`, volutil RPC types, and Coda logging. Its output should be compatible with `S_VolMakeVRDB` outside this subset.

Risks: the server writes to an arbitrary path supplied by the RPC caller, subject to process permissions. It does not initialize volutil in this function. Error detail is collapsed to `VFAIL`. No side-effect transfer is used; the file remains on the server filesystem.

Test signals: dump to a fresh path, reject existing path, permission-denied paths, empty/non-empty VRDB contents, and parse the result with the VRDB loader.
