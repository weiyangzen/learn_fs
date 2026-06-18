# sources/cloud-native/moby/daemon/logger/plugin.go

Purpose: adapts external logging plugins into the daemon logger factory.

Important APIs/types/functions: `logPlugin` interface, `RegisterPluginGetter`, `getPlugin`, `makePluginClient`, and `makePluginCreator`.

Control flow/state/persistence: `getPlugin` obtains a plugin, creates a v1 or HTTP client proxy, and returns a `Creator`. The creator makes a scoped FIFO path under `/run/docker/logging`, builds a `pluginAdapter`, queries capabilities, opens the plugin stream, creates a `LogEntryEncoder`, calls `StartLogging`, and returns a read-capable adapter when supported. On creation failure it releases the plugin.

Dependencies/integration: depends on plugin getter/client packages, `logdriver` protobuf framing, platform-specific FIFO opening, and plugin proxy RPCs.

Risks: plugin lifecycle and FIFO creation are failure-prone. Capability query failures are tolerated, so read support may be absent if capabilities cannot be fetched. Global `pluginGetter` must be registered before use.

Test signals: plugin adapter/factory tests outside this subset likely cover this; build checks validate platform variants.
