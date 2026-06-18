# sources/cloud-native/moby/integration-cli/docker_cli_links_test.go

Purpose: regression tests for legacy `--link` behavior across default networking, user-provided aliases, `/etc/hosts` injection, inspect metadata, rename/restart handling, and invalid link combinations.

Important APIs and functions: `DockerCLILinksSuite`, `testLinkPingOnNetwork`, `cli.DockerCmd`, `dockerCmdWithError`, `inspectFieldJSON`, `readContainerFileWithExec`, regex parsing of `/etc/hosts`, and sorting before comparing `HostConfig.Links`.

Control flow: tests create upstream containers, start linked consumers with aliases, then verify ping by alias, container name, and hostname. Inspect tests decode `HostConfig.Links`. Restart tests compare linked host IPs before and after upstream restart. Negative tests cover bogus targets, host-network containers, duplicate alias names, and unlinked name lookup.

State and persistence: mutates container names, link definitions, `/etc/hosts` content inside containers, bridge IP assignments, and inspect metadata. State is expected to update after rename/restart without stale link data.

Dependencies and integration points: Linux-only networking behavior, busybox ping/top, daemon link implementation, inspect JSON, `/etc/hosts` generation, and user namespace restrictions for host-network cases.

Risks: legacy links are deprecated and have network-mode-specific behavior; ping timing and DNS/hosts propagation can be flaky; duplicate alias behavior depends on resolver ordering.

Test signals: linked containers can resolve and reach expected names, inspect records exact link definitions, link host entries update after restart, and invalid combinations fail with clear conflict messages.
