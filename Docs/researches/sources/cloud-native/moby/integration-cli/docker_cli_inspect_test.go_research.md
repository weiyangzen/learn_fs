# sources/cloud-native/moby/integration-cli/docker_cli_inspect_test.go

Purpose: broad `docker inspect` integration coverage for images, containers, plugins, formatting, size fields, mounts, network settings, object lookup precedence, and error behavior.

Important APIs and functions: `DockerCLIInspectSuite`, `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `inspectFieldJSON`, `inspectFilter`, `loadSpecialImage`, typed decoders for `container.MountPoint`, `container.LogConfig`, and `image.InspectResponse`, plus `icmd` for explicit process assertions.

Control flow: tests create named containers/images, inspect specific paths or JSON blobs, decode typed output when structure matters, and verify CLI formatting. Object resolution tests cover container-vs-image precedence, `--type` filtering, invalid type values, ID prefixes, multiple object inspect with missing entries, and plugin inspection. Lifecycle state tests transition running, paused, unpaused, stopped, and committed objects before inspecting.

State and persistence: creates containers, named volumes, bind mounts, committed images, plugins, and networks. It checks persisted inspect fields such as `Created`, `State.StartedAt`, `Mounts`, `HostConfig.LogConfig`, `SizeRw`, `SizeRootFs`, image `RootFS.Layers`, and network IDs.

Dependencies and integration points: integrates with special image fixtures, busybox, plugin installation, container/image inspect API schemas, Go template rendering, and daemon-specific paths via `dPath`.

Risks: stable image ID assertions intentionally catch serialization changes but may fail when snapshotter behavior changes; template error text is brittle; plugin tests require Linux amd64 network access; mount behavior differs by OS.

Test signals: inspect must return correctly typed and formatted data, preserve timestamps as RFC3339Nano, include expected mount/network/log fields, continue inspecting valid objects when others are missing, and produce clear not-found or template errors.
