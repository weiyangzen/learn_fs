<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker.go -->
# sources/cloud-native/moby/daemon/command/docker.go

## Purpose
Builds the `dockerd` Cobra command and exposes a `Runner` abstraction used by daemon entrypoints.

## Important APIs, Types, And Functions
`newDaemonCommand`, package `init`, `Runner`, `daemonRunner.Run`, and `NewDaemonRunner`. Flags include version, config-file, common daemon flags, platform config flags, and service flags.

## Control Flow
Startup creates default config, wraps it in `daemonOptions`, configures Cobra metadata, installs flags, and runs `newDaemonCLI`. `--validate` exits after parsing with `configuration OK`; otherwise execution delegates to platform `runDaemon`.

## State And Persistence Behavior
Package init exports product name to BuildKit API caps and sets `honorXDG` when RootlessKit is detected. Runner setup changes global log format and command IO streams.

## Dependencies And Integration Points
Integrates Cobra, BuildKit API caps, rootless detection, daemon config, version metadata, platform logging, and service flag registration.

## Risks And Test Signals
Risks include config lookup during version-only paths, global rootless path policy, and flag/config coupling. Command and options tests cover flag installation and config merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/command/docker.go -->
