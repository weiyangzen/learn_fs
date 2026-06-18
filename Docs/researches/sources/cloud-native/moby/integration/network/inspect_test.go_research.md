<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/inspect_test.go -->
# sources/cloud-native/moby/integration/network/inspect_test.go

Purpose: validates verbose overlay network inspection across a multi-manager Swarm cluster before and after a leader change.

Important APIs/types/functions: `TestInspectNetwork` uses `swarm.NewSwarm`, `daemon.StartAndSwarmJoin`, `NetworkCreate` with overlay driver and IPAM config, `swarm.CreateService`, `NetworkInspect` with `Verbose` and optional `Scope`, `NodeList`, and manager restart helpers.

Control flow: the test creates three manager daemons and one worker, creates an overlay network with a constrained IPAM range, deploys a worker-only replicated service, waits for running tasks, then inspects the network by full ID, partial ID, name, and name+swarm scope from every node. It checks IPAM config, manager-only global IPAM status counters, and worker-local service task details. It then forces a leader change by restarting the current leader and repeats the inspection checks.

State/persistence: creates a Swarm cluster, overlay network, VXLAN kernel state, service tasks, and cluster IPAM state. Cleanup removes the network and polls until it is removed from the worker to avoid VXLAN leakage across tests.

Dependencies/integration: Swarm test helpers, daemon harness, API client, `networktypes.SubnetStatus`, poll helpers, and rootless/Windows skips.

Risks: multi-daemon swarm tests are slow and sensitive to leader election timing, VXLAN cleanup, and local kernel state. IPAM counter expectations encode knowledge of manager/worker/task endpoint reservations.

Test signals: passing tests show overlay network inspect remains consistent by ID/name/scope, manager status survives leader change, and worker-local service information is available where the network is instantiated.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/inspect_test.go -->
