# sources/distributed-fs/ipfs-kubo/core/node/helpers.go

Purpose: provides small fx helpers for lifecycle hooks and conditional option assembly. Important APIs are `lcStartStop.Append`, `maybeProvide`, and `maybeInvoke`.

Control flow: `lcStartStop.Append` accepts a function that starts work and returns a stop function. It installs fx `OnStart` and `OnStop` hooks, skips work when the passed context is already done, stores the stop closure, and errors if stop is unexpectedly nil. `maybeProvide` and `maybeInvoke` return the corresponding fx option only when enabled.

State and persistence: stores only one in-memory `stopFunc` closure per appended hook. No datastore or filesystem state is touched.

Dependencies and integration: depends on `context`, `errors`, and `go.uber.org/fx`. It is used by IPNS republisher and conditional graph composition across `groups.go`.

Risks: the stop function is unbounded and context is not passed to it; callers must make their own shutdown behavior safe. The typo in error text (`lcStatStop`) is harmless but could make logs less searchable. There are no direct tests in this subset; integration tests that start/stop fx apps are the primary signal.
