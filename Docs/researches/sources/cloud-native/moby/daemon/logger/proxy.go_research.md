# sources/cloud-native/moby/daemon/logger/proxy.go

Purpose: RPC proxy for logging plugin methods.

Important APIs/types/functions: `client`, `logPluginProxy`, request/response structs, `StartLogging`, `StopLogging`, `Capabilities`, and `ReadLogs`.

Control flow/state/persistence: methods marshal requests to plugin RPC method names, map non-empty response `Err` strings to Go errors, and return read streams for `ReadLogs`.

Dependencies/integration: used by `plugin.go` for both v1 and HTTP plugin clients.

Risks: plugin errors are stringly typed. ReadLogs streaming error behavior depends on plugin client implementation.

Test signals: plugin proxy tests outside this subset likely cover method names and error mapping.
