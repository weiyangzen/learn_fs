# sources/distributed-fs/lizardfs/src/master/hstorage_init.cc

Purpose: initializes and owns the process-global `hstorage::Storage` backend used by `hstorage::Handle` name strings.

Important APIs/types/functions: `hstorage_init()` reads storage config, chooses Berkeley DB or memory backend, registers reload/destruct callbacks, and returns success; `hstorage_reload()` warns when storage-related options change at runtime and require restart; `hstorage_term()` resets the global storage.

Control flow: initialization reads `USE_BDB_FOR_NAME_STORAGE`, `DATA_PATH`, and `BDB_NAME_STORAGE_CACHE_SIZE`; if BDB is requested and compiled in it opens `name_storage.db`, otherwise it logs and falls back to `MemStorage`. Reload compares new config values with saved globals and logs non-reloadable changes.

State and persistence behavior: globals store selected backend flag, BDB path, and cache size. `Storage::reset()` installs or destroys the backend. BDB name storage writes a heap database under the data path; memory storage is volatile.

Dependencies/integration: depends on config/event loop, `MemStorage`, optional `BDBStorage`, setup path constants, and syslog. `init.h` requires this module to run first because directory-entry handles depend on an active storage implementation.

Risks and test signals: config key mismatch exists between reload (`USE_BDB_NAME_STORAGE`) and init (`USE_BDB_FOR_NAME_STORAGE`), so reload warnings may not reflect the real init option. Resetting storage while handles still exist would break destructors. Tests should cover backend selection with/without libdb, fallback logging, restart-required warnings, and init ordering.
