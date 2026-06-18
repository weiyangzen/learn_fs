# sources/distributed-fs/eos/mgm/proc/admin/Monit.cc

Purpose: Implements the legacy opaque-parameter monitoring admin command for Prometheus endpoint configuration.

Important APIs/types/functions: `ProcCommand::Monit()` reads `mgm.subcmd`, `mgm.monit.service`, `mgm.monit.port`, and `mgm.monit.cache_ttl`. It uses monitoring helpers `ParsePortConfig()`, `ParseUint32Config()`, `IsValidCacheTtl()`, and constants for Prometheus global config keys. It calls `gOFS->GetMonitoringConfig()` and `gOFS->ApplyMonitoringConfig()`.

Control flow: Only service `prometheus` is accepted. `ls`, `list`, and `status` return current config. Mutating commands require master MGM. `enable` validates or requires a configured port, optionally validates cache TTL, sets the enabled flag, and applies the config. `disable` clears the enabled flag and applies. Unsupported subcommands return `EINVAL`.

State and persistence behavior: Monitoring settings are stored as global `FsView` config values (`kPrometheusPortConfig`, `kPrometheusCacheTtlConfig`, `kPrometheusEnabledConfig`). `ApplyMonitoringConfig()` applies them to the running MGM monitoring service. Persistence is through the global config mechanism, not local members.

Dependencies and integration points: Depends on `FsView`, `MonitoringConfig.hh`, `XrdMgmOfs`, and legacy `ProcCommand`. It coexists with the newer protobuf `MonitCmd` implementation and should remain behavior-compatible where possible.

Risks: Legacy enable requires an existing or supplied port, while `MonitCmd::EnableSubcmd()` defaults the port if missing. Only master checks protect mutation; read access is open. Cache TTL parse accepts string input and must be kept aligned with protobuf validation.

Test signals: Unsupported service, list aliases, master-only mutation, enable with missing port, port range validation, cache TTL range validation, disable, apply failure propagation, and compatibility with protobuf monitoring command output.
