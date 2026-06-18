## sources/cloud-native/moby/integration-cli/docker_cli_volume_test.go

Purpose: comprehensive CLI coverage for Docker volumes: create, inspect, list formats, filters, remove/force behavior, labels, driver/options, in-use semantics, and duplicate mountpoint resolution for `--volumes-from`, binds, and API mounts.

Important APIs and helpers include `DockerCLIVolumeSuite`, `assertVolumesInList`, CLI wrappers, Go client `ContainerCreate`, `container.HostConfig`, `mount.Mount`, and `network.NetworkingConfig`. Control flow creates volumes and containers, runs commands with `-v` or `--volumes-from`, inspects volume/containers, and sometimes manipulates the local volume directory to simulate missing mountpoints.

State and persistence are core: named volumes retain data across container removal, labels/options persist in volume metadata, and in-use reference counts include both created and started containers. Dependencies include local daemon access for some tests, Linux tmpfs mount semantics, and build helper images. Risks include host filesystem mutation, filter output assumptions, and legacy mount conflict behavior that is intentionally preserved. Test signals are volume list/inspect output, error messages, persisted `hello` data, tmpfs mount options, label filtering, and absence/presence of volume references after duplicate-target scenarios.
