# sources/cloud-native/soci-snapshotter/integration/run_test.go

Purpose: validates runtime behavior after SOCI pulls: multi-container execution, retry behavior under registry network loss, permissions, restartability, content-store and namespace isolation, converted-image runs, and idmapped snapshots.

Important APIs and flow: `TestRunMultipleContainers` pulls SOCI images, runs multiple containers, checks no overlay fallback, probes web services, and verifies unique overlay upper/work dirs. `TestNetworkRetry` blocks registry IP with iptables to test blob retry configuration and cached-span behavior. `TestRootFolderPermission` checks non-root users can read `/`. `TestRestartAfterSigint` kills and manually restarts the snapshotter. `TestRunInContentStore` and `TestRunInNamespace` enforce content-store and namespace matching. `TestRunAfterConvert` runs images converted by online and standalone convert with SOCI v2 enabled. `TestRunWithIdMap` configures subuid/subgid, runs userns-remapped containers under FUSE/mixed/no-index modes, and checks host and container UID/GID views.

State and persistence: creates registry images, indexes, containers, FUSE mounts, idmapped snapshot directories, iptables rules, users/groups, subuid/subgid files, and runtime tasks.

Dependencies and integration: integrates SOCI snapshotter, containerd/nerdctl, local registries, metrics, iptables, Linux user namespaces, content stores, namespaces, and idtools remapping.

Risks and test signals: deep runtime coverage with significant environmental risk. Tests depend on containerd version for idmap support, network timing, process kill timing, and cleanup of iptables and containers.
