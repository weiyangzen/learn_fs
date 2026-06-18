# sources/distributed-fs/openafs/src/util/dirpath_nt.h

Purpose: Defines the OpenAFS directory path contract: canonical path constants, file-name constants, path id enumeration, and convenience macros that route local paths through `afs_getDirPath()`. Despite the `_nt` suffix, it is the primary public header for the dirpath abstraction across platforms.

Important APIs and types: Declares `initAFSDirPath()`, `ConstructLocalPath()`, `ConstructLocalBinPath()`, `ConstructLocalLogPath()`, `afs_getDirPath()`, and legacy `getDirPath()`. Defines `afsdir_id_t`, with ids for server directories, client directories, and many server/client files such as `AFSDIR_SERVER_KEY_FILEPATH_ID`, `AFSDIR_CLIENT_CELLSERVDB_FILEPATH_ID`, and `AFSDIR_SERVER_EXT_KEY_FILEPATH_ID`.

Control flow and state: This header has no runtime state, but it defines the index order that must exactly match `dirpath.c` population. Macros like `AFSDIR_SERVER_LOGS_DIRPATH` perform a function call into the initialized table, so callers implicitly depend on lazy initialization and the static table lifetime.

Dependencies and integration: Includes `afs/param.h`, `limits.h`, and `windef.h` on Windows. It is central to server logging, config lookup, bosserver-related code, cache-manager config, and command-line tools that need canonical versus local path behavior.

Risks and test signals: The enum is an ABI/behavioral contract; adding or reordering ids without updating `dirpath.c` breaks macro results. Some macros are duplicated (`AFSDIR_SERVER_LOCAL_DIRPATH`, `AFSDIR_SERVER_MIGRATE_DIRPATH`), which is harmless for preprocessing but a maintenance smell. `dirpath_test` prints many macros and gives a direct smoke test for header/table consistency.
