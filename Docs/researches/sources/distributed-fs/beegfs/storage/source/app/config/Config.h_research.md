## sources/distributed-fs/beegfs/storage/source/app/config/Config.h

Purpose: Declares storage daemon configuration fields and accessors.

Important APIs/types/functions: `Config` extends `AbstractConfig` with storage directories, filesystem UUIDs, first-run init policy, stream/worker counts, buffer sizes, NUMA and priority settings, file IO sizes, per-user/per-target queue toggles, cache limits, resync slave counts, aggressive polling, chunk balance queue limit, quota flags, resync/offline timing, daemonization, and PID file.

Control flow: Header declares overrides for defaults, parsing, implicit values, and default filename lookup. Getters expose parsed values; `setQuotaEnableEnforcement()` allows mgmtd quota policy to override local config at runtime.

State and persistence: Stores parsed configuration in memory. Some values control persistent safety behavior such as filesystem UUID checks and target initialization.

Dependencies and integration: Depends on common `AbstractConfig` and compile-time detection of `sync_file_range` support. Consumed broadly by `App`, `InternodeSyncer`, storage IO, benchmarker, and resyncer.

Risks and test signals: Runtime mutation of quota enforcement means config is not immutable after startup. Tests should verify getters reflect parsed values and mgmtd quota override behavior.
