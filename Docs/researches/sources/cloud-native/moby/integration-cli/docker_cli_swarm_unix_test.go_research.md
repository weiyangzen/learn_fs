## sources/cloud-native/moby/integration-cli/docker_cli_swarm_unix_test.go

Purpose: Unix-only swarm plugin coverage. `TestSwarmVolumePlugin` verifies a service task remains pending when a requested volume plugin is missing, then schedules once the plugin is available. `TestSwarmNetworkPluginV2` validates global network plugin scheduling across manager and worker nodes and behavior after disabling the plugin on one node.

Control flow starts swarm daemons, creates services/networks with plugin drivers, polls task states and active container counts, inspects container mounts, and installs/disables a v2 plugin by name. State includes plugin availability, service task scheduling, overlay/global network membership, and volume mount metadata.

Dependencies are suite plugin helpers such as `newVolumePlugin`, daemon CLI wrappers, swarm task-state checks, `reducedCheck`, and amd64-only plugin image availability. Risks include external plugin image availability, 20-second fixed sleep after plugin disable, plugin lazy loading, and long swarm reconciliation delays. Test signals are pending task error `missing plugin on 1 node`, one running task after plugin load, mount `Name`/`Driver`, and only one global-service instance when one node lacks the network plugin.
