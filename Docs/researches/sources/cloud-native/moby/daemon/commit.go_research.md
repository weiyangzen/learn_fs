<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/commit.go -->
# sources/cloud-native/moby/daemon/commit.go

## Purpose
Implements container-to-image commit and config merge semantics between user changes and the original container image/container config.

## Important APIs, Types, And Functions
`merge` mutates a user config with image defaults. `Daemon.CreateImageFromContainer` performs commit validation, optional pause/unpause, Dockerfile-style config changes, image service commit/tag, event logging, and metrics.

## Control Flow
`merge` fills missing user, ports, env, labels, entrypoint/cmd, healthcheck fields, working dir, volumes, and stop signal. Commit rejects dead/removing containers and running Windows containers, pauses unless disabled or already paused, builds a new config from changes, merges old container config, commits through image service, tags if requested, and logs a commit event.

## State And Persistence Behavior
May pause/unpause the container, creates a persistent image, optionally writes a tag reference, logs events, and updates `metrics.ContainerActions`.

## Dependencies And Integration Points
Integrates daemon container lookup, Dockerfile config builder, image service, distribution references, events, errdefs, and metrics.

## Risks And Test Signals
Risks include merge precedence bugs, Windows running-commit restriction, pause failure ignored, and volume map copy direction preserving image volumes only if user map is initialized. Commit API and image tests outside this file are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/commit.go -->
