# sources/cloud-native/nydus/contrib/nydusify/pkg/hook/hook_test.go

Purpose: validates hook RPC adapters, plugin wrapper construction, initialization no-op paths, environment path behavior, and RPC round trips.

Important fixtures/APIs: `fakeHook`, `RPCServer.BeforePushManifest`, `RPCServer.AfterPushManifest`, `Plugin.Server`, `Plugin.Client`, `Init`, `Close`, and `RPC` client methods.

Control flow and state: tests preserve and restore global `Caller`, `hookPluginPath`, and `client`. They validate that initialized callers prevent plugin loading, missing paths leave `Caller` nil, stat errors are logged without panics, and a net.Pipe RPC server/client can dispatch before/after calls and propagate hook errors.

Dependencies and integration points: net/rpc, net.Pipe, go-plugin mux broker types, testify require, and process-global hook state.

Risks and test signals: tests do not execute a real external plugin process, so handshake, process startup, and binary compatibility are not covered. They do document the silent no-op behavior for absent hook binaries.
