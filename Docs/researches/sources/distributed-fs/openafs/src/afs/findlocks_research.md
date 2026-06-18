# sources/distributed-fs/openafs/src/afs/findlocks

Purpose: developer utility script for scanning source trees for OpenAFS lock acquisition source-indicator numbers and reporting duplicates.

Important APIs/types: Perl script using `File::Find` and `IO::File`. Pattern matches `ObtainLock`, `ObtainWriteLock`, `ObtainSharedLock`, `NBObtainLock`, `NBObtainWriteLock`, `NBObtainSharedLock`, and `UpgradeSToWLock` calls with a numeric second argument.

Control flow: optional `-d` restricts output to duplicate lock IDs. The script recursively visits input paths, records `path:line` per numeric lock ID, then prints IDs in numeric order with all locations.

State and persistence: no persistent state; all results are in-memory arrays for one run.

Dependencies and integration points: supports the `lock.h` convention where write/shared/upgrade acquisition records `src_indicator`. It is useful when maintaining `MAX_LOCK_NUMBER` and avoiding duplicate diagnostic IDs.

Risks: regex-based scanning misses multi-line/unusual macro invocations and can produce false positives in comments or strings. It assumes lock ID arguments are literal integers.

Test signals: run against `src/afs` with and without `-d`; verify known duplicate and unique lock IDs; include files with no lock calls and nested directories.
