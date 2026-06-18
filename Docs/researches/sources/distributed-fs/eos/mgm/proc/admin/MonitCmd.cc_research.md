# sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.cc

Purpose: Implements protobuf-backed monitoring administration for listing, setting, enabling, and disabling the Prometheus monitoring endpoint.

Important APIs/types/functions: `MonitCmd::ProcessRequest()` dispatches `MonitProto` oneof cases. `ConfigSubcmd()` dispatches config `ls` and `set`. `ConfigLsSubcmd()` returns `gOFS->GetMonitoringConfig()`. `ConfigSetSubcmd()` validates port and cache TTL, updates global config, and applies. `EnableSubcmd()` ensures a default Prometheus port when absent, sets enabled, and applies. `DisableSubcmd()` clears enabled and applies.

Control flow: Unsupported command or config oneof cases return `EINVAL`. All mutations require `gOFS->mMaster->IsMaster()`. Each mutating path updates `FsView::gFsView` global config first, then calls `ApplyMonitoringConfig()` and returns the refreshed configuration on success.

State and persistence behavior: State is global MGM monitoring config in `FsView` using `MonitoringConfig.hh` keys and defaults. Runtime application is delegated to `XrdMgmOfs::ApplyMonitoringConfig()`. The command object is stateless apart from inherited request identity.

Dependencies and integration points: Depends on generated `Monit.pb.h`, `FsView`, `MonitoringConfig.hh`, and `XrdMgmOfs`. It is the protobuf counterpart to `ProcCommand::Monit()`.

Risks: Behavior differs from legacy `Monit.cc` by auto-populating `kDefaultPrometheusPort` on enable. `DisableSubcmd()` ignores its proto payload, so future fields would need explicit handling. Applying after partial config changes can leave global config updated even when runtime apply fails.

Test signals: Dispatch errors, config list, master authorization, port/cache TTL validation, default port creation on enable, disable, apply failure, output shape after each success, and compatibility with legacy command state.
