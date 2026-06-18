# sources/cloud-native/moby/integration/container/create_test.go

Purpose: Broad integration coverage for container creation validation, image identifier handling, host config validation, healthcheck constraints, platform selection, network endpoint behavior, MAC assignment, and containerd image metadata.

Important APIs and flow: Tests use `apiClient.ContainerCreate`, `ImageInspect`, `ContainerInspect`, `ContainerStart`, raw `request.Post`, and direct containerd client inspection. Cases cover missing images, image IDs with and without algorithms, links to missing containers, invalid env values, tmpfs targets, masked/readonly path defaults from `oci.DefaultSpec`, invalid healthcheck durations/retries, tmpfs overriding anonymous volumes, platform mismatch errors, `VolumesFrom`, invalid host config modes, JSON body validation, multi-endpoint API-version behavior, per-network MACs, and containerd-backed `ctr.Image`.

State and dependencies: The tests create and sometimes start containers, create networks, build no persistent custom daemon except containerd inspection through `Info().Containerd`. They depend on busybox, API versions, Linux-only behavior for proc paths/tmpfs/MACs, and containerd namespace details.

Risks and signals: This file is a high-value compatibility net for API validation and versioned behavior. It catches regressions in error typing, default OCI path persistence across start/inspect, platform manifest decisions, old/new network API contracts, and containerd metadata when snapshotter storage is enabled.
