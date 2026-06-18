# sources/distributed-fs/lizardfs/utils/slow_chunk_scan.c

Purpose: LD_PRELOAD test shim that slows directory scans except for selected chunk storage directories. It exercises timeout and scheduling behavior during chunk scanning.

Important APIs/functions: overrides `opendir`, `readdir_r`, and `closedir`. `opendir()` records `DIR*` handles whose path contains one of `hdd_0_0` through `hdd_3_0` in a fixed `fast_dir` table. `readdir_r()` sleeps one second unless the handle is in the fast table. `closedir()` removes handles from the table.

Control flow: every opened directory is checked for fast path substrings. `readdir_r()` holds a mutex while scanning the handle table, then either sleeps or proceeds to the real `readdir_r`.

State and persistence: process-local static array of up to 5000 fast directory handles, protected by `pthread_mutex_t`. No persistent output.

Dependencies/integration: intended for Linux/glibc test processes via `LD_PRELOAD`. It targets code paths still using `readdir_r`.

Risks and test signals: `readdir_r` is deprecated in modern libc. The fixed table silently stops tracking fast dirs once full. If `opendir` fails and returns NULL, NULL may be recorded for matching paths. Test signals are slow scans for generic dirs, fast scans for named hdd paths, handle cleanup on `closedir`, and concurrent scans.
