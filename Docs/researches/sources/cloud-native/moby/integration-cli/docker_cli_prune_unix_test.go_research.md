# sources/cloud-native/moby/integration-cli/docker_cli_prune_unix_test.go

Purpose: Unix prune coverage for networks, images, containers, and volumes, including filters from CLI flags and Docker config defaults.

Important APIs and functions: `DockerCLIPruneSuite` teardown/timeout, helper `pruneNetworkAndVerify`, `DockerSwarmSuite.TestPruneNetwork`, daemon commands, `cli.BuildCmd`, `build.WithDockerfile`, `poll.WaitOn`, checker predicates, temp config files containing `pruneFilters`, and `daemonUnixTime`.

Control flow: network prune creates unused and in-use bridge/overlay networks, attaches a container and service, prunes, and polls kept/pruned results. Image prune distinguishes dangling vs `--all`, then label filters. Container and volume prune create resources with labels, use config-level `pruneFilters`, override with CLI `label` and `label!=` filters, and verify remaining resources. Network label prune tests include equality and inequality filters.

State and persistence: creates swarm services, networks, containers, volumes, images, temp Docker configs, and daemon-specific image stores. Tests assert destructive prune commands remove only eligible resources.

Dependencies and integration points: local daemon/swarm suite, busybox, build helper, Docker config parsing, prune filter implementation, reconciliation timing, and poll utilities.

Risks: destructive by design; requires isolation from unrelated resources. Timing around service/container activity and image dangling status can be flaky if cleanup or build behavior changes.

Test signals: prune commands must respect in-use protections, dangling/all semantics, until filters, label and label-not filters, and CLI filters overriding configured prune filters.
