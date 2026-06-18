# sources/distributed-fs/openafs/src/util/dirpath.c

Purpose: Implements the runtime directory path table used by OpenAFS utilities and servers to map canonical AFS paths such as `/usr/afs/bin` and `/usr/afs/etc` onto local install paths. It exists primarily to support Windows installations with configurable roots while preserving Unix and wire-format path compatibility.

Important APIs and functions: `initAFSDirPath()` initializes the path table and returns `AFSDIR_CLIENT_PATHS_OK` / `AFSDIR_SERVER_PATHS_OK`; `afs_getDirPath()` exposes indexed strings; Windows also exports `getDirPath()` for ABI compatibility. `ConstructLocalPath()`, `ConstructLocalBinPath()`, and `ConstructLocalLogPath()` convert canonical or relative paths into allocated local paths. Internal helpers include `initDirPathArray()` and `LocalizePathHead()`.

Control flow and state: The module maintains static `dirPathArray`, `initFlag`, `initStatus`, and top-level server/client path buffers. Under pthreads, initialization is guarded by `pthread_once`; otherwise it is lazy but not otherwise synchronized. Windows initialization reads server/client install/config paths through `afssw_GetServerInstallDir()` and `afssw_GetClientCellServDBDir()`, normalizes paths, derives short-path variants, then populates every path id. Unix uses compile-time canonical paths, with Darwin alternate client paths if present.

Dependencies and integration: Depends on `afsutil.h`, `fileutil.h`, roken, `afs/opr.h`, Windows registry/install APIs under `AFS_NT40_ENV`, and path macro/id definitions from `dirpath_nt.h`. Other subsystems use the exported macros to locate logs, databases, cell config, server binaries, and migration files.

Risks and test signals: The static arrays are fixed-size and rely on `strcompose`, `strcpy`, `strcat`, and `sprintf` usage staying within `AFSDIR_PATH_MAX`. Invalid `afsdir_id_t` values are not bounds checked. `ConstructLocalPath()` returns allocated memory that callers must free. `util/test/dirpath_test.c` exercises path table output and local path construction.
