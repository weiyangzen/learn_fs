# sources/cloud-native/moby/integration/service/plugin_test.go

## Purpose
Validates Swarm plugin services across a multi-node cluster: plugin image distribution through a local registry, environment propagation, service update to a new plugin reference, removal cleanup, placement constraints, and default naming when plugin spec name is omitted.

## Important APIs, Types, And Functions
- `TestServicePlugin` builds/pushes two plugin references, starts two managers and one worker, creates plugin-runtime services, and polls plugin state on each node.
- `makePlugin` mutates a `swarmtypes.Service` to use `RuntimePlugin`, sets `PluginSpec` remote/name/env, and optional placement constraints.
- Daemon helper pollers `PluginIsRunning`, `PluginReferenceIs`, and `PluginIsNotPresent` provide node-level checks.

## Control Flow
The test first uses a regular daemon to create and push two plugin artifacts to a local registry. It then starts a three-node experimental Swarm, creates a plugin service, validates plugin installation/running on all nodes and env filtering, updates to the second reference, removes it, repeats with manager-only constraints, and repeats with no explicit plugin name.

## State And Persistence
State includes local registry content, plugin images, cluster services/tasks, node-local plugin installations, plugin settings/env, and service placement. Cleanup stops daemons and removes services, but registry artifacts exist only for the test registry lifetime.

## Dependencies And Integration Points
Requires local daemon control, amd64, non-Windows, non-remote execution, experimental daemon mode, plugin fixture creation, registry fixture, Swarm multi-node join, and plugin management API support.

## Risks And Edge Cases
Environment- and architecture-sensitive. Plugin installation/update/removal is asynchronous across nodes. Invalid env entries are expected to be ignored while valid `foo=bar` remains. Placement constraints must avoid installing on workers.

## Test Signals
Passing requires plugin running on expected nodes, reference updating to `repo2`, plugin removal on all nodes, manager-only constraints excluding the worker, and plugin spec env containing `foo=bar` without invalid `baz`.
