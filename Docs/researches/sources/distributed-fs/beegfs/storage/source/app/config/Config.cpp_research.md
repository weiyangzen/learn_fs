## sources/distributed-fs/beegfs/storage/source/app/config/Config.cpp

Purpose: Implements storage daemon configuration defaults, parsing, implicit value derivation, and default config-file lookup.

Important APIs/types/functions: `loadDefaults()` defines storage-specific keys for interfaces, target directories, filesystem UUIDs, worker/listener tuning, IO sizes, resync slave counts, quotas, offline/resync safety thresholds, daemonization, and PID file. `applyConfigMap()` parses typed values, validates `logType`, comma-splits storage directories and UUIDs, enforces `sysTargetOfflineTimeoutSecs >= 30`, and removes handled keys. `initImplicitVals()` derives read-ahead trigger size, interface list, socket buffers, sync-file-range support, and auth hash. `createDefaultCfgFilename()` returns `/etc/beegfs/beegfs-storage.conf` if present.

Control flow: Parsing delegates common settings to `AbstractConfig::applyConfigMap(false)` first, then iterates the remaining map and either consumes known storage keys or throws on unknown keys if enabled.

State and persistence: Holds parsed runtime configuration. It does not persist config; it reads files through the abstract config layer and checks default file existence.

Dependencies and integration: Uses `StringTk`, `UnitTk`, `Path`, POSIX `stat`, and `AbstractConfig`. Values are consumed by `App`, workers, storage targets, benchmarker, resyncer, quota logic, and internode syncer.

Risks and test signals: Comma-splitting storage paths means paths containing commas are unsupported. Distro-dependent `sync_file_range` validation changes behavior at compile time. Tests should cover invalid log type, missing/empty target dirs, UUID list parsing, offline timeout lower bound, human-size parsing, and unknown-key exception behavior.
