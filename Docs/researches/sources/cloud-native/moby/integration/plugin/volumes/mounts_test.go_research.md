# sources/cloud-native/moby/integration/plugin/volumes/mounts_test.go

## Purpose
Regression test for plugin mount ordering involving `/dev` mounts and other bind mounts. It verifies a plugin with host/dev binds and propagated mount settings can be enabled.

## Important APIs, Types, And Functions
Uses local daemon with iptables disabled, volume `createPlugin`, dummy binary, `asVolumeDriver`, plugin config mutation for `Mounts`, `PropagatedMount`, host networking, and `IpcHost`, then `PluginEnable`, `PluginInspect`, and `PluginRemove`.

## Control Flow
The test creates a temporary directory, creates a plugin with bind mounts for `/` to `/host`, `/dev` to `/dev`, and temp dir to `/etc/foo`, sets propagated mount and host namespace options, enables the plugin, inspects it, and asserts it is enabled.

## State And Persistence Behavior
State includes daemon plugin config, bind mount metadata, and a temporary directory. The plugin is removed in cleanup.

## Dependencies And Integration Points
Depends on local non-rootless Linux daemon, plugin fixture mounting behavior, volume driver capability metadata, and mount ordering inside daemon plugin setup.

## Risks
Requires privileges for host mounts and is skipped for rootless/Windows/remote daemons. It validates enablement rather than volume operations, so it targets a narrow regression.

## Test Signals
Signals are successful plugin creation/enabling and `PluginInspect` reporting `Enabled`.
