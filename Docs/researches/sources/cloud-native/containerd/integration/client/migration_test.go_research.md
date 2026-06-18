<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/migration_test.go -->
# sources/cloud-native/containerd/integration/client/migration_test.go

## Purpose
Tests `containerd config migrate` against the current default config and selected historical fixtures, ensuring old defaults and custom values migrate to the current generated default shape.

## APIs, Types, And Functions
`TestMigration` drives the command-line `containerd config default` and `containerd -c <file> config migrate`. Helpers are `currentDefaultConfig`, `replaceAllValues`, and `replaceValue`.

## Control Flow And State
The test writes the current default config to a temp file and always checks that migrating it is identity-preserving. On linux/amd64 builds whose default includes btrfs and devmapper, it also migrates `default-1.6.toml`, `default-1.7.toml`, and `custom-1.7.toml`. The custom expected output is derived by replacing selected current-default values such as sandbox image, streaming address/port/timeouts, and TLS streaming.

## Persistence And Integration Points
The test persists only temp config files and reads fixture TOML files. It integrates with the `containerd` binary, server config defaults, migration code, and fixture comments documenting removed or changed settings.

## Risks And Test Signals
Failures indicate unstable default config generation, incomplete migration rules, accidental loss of custom CRI stream/sandbox values, platform-dependent fixture mismatch, or a missing/broken `containerd` binary in PATH.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/migration_test.go -->
