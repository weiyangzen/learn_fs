# Research: sources/cloud-native/moby/daemon/cluster/executor/container/executor.go

## sources/cloud-native/moby/daemon/cluster/executor/container/executor.go

Purpose: implements the SwarmKit `exec.Executor` for Moby. It describes the local node to swarmkit, configures ingress and node network attachments, chooses the right task controller, propagates network encryption keys, and exposes dependency managers for secrets, configs, and volumes.

Important types and APIs: `executor`, `NewExecutor`, `Describe`, `Configure`, `Controller`, `SetNetworkBootstrapKeys`, `Secrets`, `Configs`, `Volumes`, and `sortedPlugins`. `Describe` queries daemon system info, normalizes labels, merges v1 and enabled v2 plugin capabilities, adds built-in overlay networking, queries CSI node info, and stores an `api.NodeDescription` under a mutex. `Configure` reads swarm node attachments, sets up or releases ingress, tracks removed or changed attachment IPs, deletes stale managed load-balancer networks when possible, updates the previous node object, and resets the backend attachment store.

Controller selection is runtime-dependent. Network attachment tasks use `newNetworkAttacherController`; generic plugin-runtime tasks require experimental mode and use the plugin controller; container tasks use `newController`; unsupported runtimes return errors. State includes backend references, a SwarmKit dependency manager, cached node description, and cached node object for attachment-diffing.

Dependencies include daemon executor backends, plugin backend, cluster convert package, libnetwork, network encryption types, SwarmKit agent/dependency/template APIs, and plugin discovery. Risks include ignored CSI node-info errors, malformed attachment entries that are skipped, stale `nodeObj` assumptions, partial cleanup when active endpoints prevent removal, and runtime behavior depending on experimental mode. Test coverage here is indirect; this file is exercised by swarm integration paths rather than direct unit tests in this subset.
