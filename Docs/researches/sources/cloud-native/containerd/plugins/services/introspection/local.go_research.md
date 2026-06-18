# sources/cloud-native/containerd/plugins/services/introspection/local.go

## Purpose
Registers and implements the local introspection service for plugin inventory, server identity, deprecation warnings, and plugin-specific extra info.

## Important APIs, Types, And Functions
`Local` stores plugin set, root, plugin cache, and warning client. Methods include `UpdateLocal`, `Plugins`, `Server`, `PluginInfo`, `getUUID`, `generateUUID`, `pluginToPB`, `pluginsToPB`, `warningsPB`, and `adaptPlugin`.

## Control Flow
Startup gets the deprecations warning service and captures the plugin set/root. `Plugins` parses filters and returns matching cached plugin protos. `Server` returns persisted daemon UUID, process ID, Linux PID namespace inode when available, and warning list. `PluginInfo` looks up a plugin, returns base metadata, optionally instantiates the plugin and calls its `PluginInfo` provider, then marshals extra data.

## State And Persistence
Persists a daemon UUID at `<root>/uuid`, generating it if missing or empty. Caches plugin protobufs in memory until plugin count changes. Warning state comes from the warning service.

## Dependencies And Integration Points
Requires warning/deprecation service. Integrates with plugin registry, filters, errgrpc/status conversion, typeurl, protobuf timestamps, OS process info, and platform-specific `statPIDNS`.

## Risks
Plugin cache invalidation only checks count, not metadata mutations. UUID file is written with mode `0666` subject to umask. Extra plugin info is unavailable for failed plugins and depends on optional provider interface.

## Test Signals
No direct tests in this subset.
