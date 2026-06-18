## sources/cloud-native/moby/integration-cli/docker_cli_service_create_test.go

Purpose: verifies `docker service create` behavior for swarm services on non-Windows daemons, especially volume/tmpfs mounts, secrets, configs, and network aliases. Important entry points are `DockerSwarmSuite` tests such as `TestServiceCreateMountVolume`, the secret/config target-path tests, duplicate-reference tests, `TestServiceCreateMountTmpfs`, and `TestServiceCreateWithNetworkAlias`.

Control flow: each test creates a swarm daemon with `s.AddDaemon(ctx, c, true, true)`, issues CLI commands, then polls swarm task state until a task has node and container status. It inspects service specs and concrete containers, unmarshalling JSON into `mount.Mount`, `container.MountPoint`, `swarm.SecretReference`, and `swarm.ConfigReference`.

State and persistence: secrets/configs are created through the API and attached into task files; volumes persist as Docker volumes; tmpfs is runtime-only. Dependencies include swarm API types, CLI helpers, `poll`, and suite `nodeCmd`. Risks are polling races, unordered map iteration, and platform-only semantics. Test signals are spec fields, mounted file contents, `HostConfig.Mounts`, `Mounts`, and alias lists.
