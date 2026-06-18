# sources/cloud-native/moby/integration-cli/docker_api_containers_test.go

## Purpose
Large legacy API integration suite for container list, inspect, export, diff, stats, pause/top, commit, create/start/stop/wait/remove, archive copy, resource validation, and mount behavior.

## Important APIs and Types
Defines many `DockerAPISuite` tests, helper `ChannelBuffer`, `UtilCreateNetworkMode`, and `containerExit`.

## Control Flow, State, and Persistence
Tests create containers through client and raw HTTP requests, start/stop/remove them, stream stats, inspect JSON, export tar archives, validate headers and null JSON handling, check resource validation errors, and exercise mount validation and creation for bind, volume, tmpfs, local driver options, propagation, NoCopy, anonymous volume removal, named volume persistence, and custom stop-signal kill behavior.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker client API, CLI helpers, daemon platform predicates, filesystem temp dirs, volume service, network/resource validation, and poll helpers. It mutates containers, images, volumes, and host temp mounts. Risks include timing-sensitive stats streams, platform branches, leaked volumes, and brittle expected error text. It is the main signal for daemon container API compatibility, especially mount behavior tied to `daemon/volumes.go`.
