# sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook.go

Purpose: defines an optional HashiCorp go-plugin hook mechanism for invoking external logic before and after manifest push operations.

Important APIs/types/functions: `Blob`, `Info`, `Hook`, RPC client/server adapters, `Plugin`, global `Caller`, handshake config, `NewPlugin`, `Init`, and `Close`.

Control flow: package init sets `hookPluginPath` from `NYDUS_HOOK_PLUGIN_PATH` if present. `NewPlugin` serves an implementation under plugin key `hook`. `Init` is idempotent when `Caller` is already set, skips missing plugin binaries, creates a plugin client for an executable path, dispenses the hook implementation, and assigns it to global `Caller`. `Close` kills the plugin client if present.

State and persistence: global mutable state includes plugin path, plugin client, and caller implementation. Hook info carries bootstrap path, source/target refs, and blob IDs/sizes; no persistence is performed by this package.

Dependencies and integration points: `net/rpc`, HashiCorp go-plugin/hclog, `os/exec`, logrus, environment configuration, and pack/conversion push workflows that call `Caller`.

Risks and test signals: global state is process-wide and not synchronized. Failed client creation logs and returns silently, which makes hooks best-effort. Plugin executable trust and handshake configuration are operational concerns.
