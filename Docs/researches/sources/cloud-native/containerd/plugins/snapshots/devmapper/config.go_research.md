# sources/cloud-native/containerd/plugins/snapshots/devmapper/config.go

## Purpose
`config.go` defines and validates devmapper snapshotter configuration.

## Important APIs, Types, And Functions
`Config` includes root path, pool name, base image size string and parsed bytes, async remove, discard blocks, filesystem type, and filesystem options. `LoadConfig` reads TOML, `parse` converts base image size and defaults filesystem type, and `Validate` checks required fields and supported filesystems.

## Control Flow
`LoadConfig` opens the path, decodes TOML, parses sizes/defaults, validates, and returns the config. Validation accumulates multiple errors through `errors.Join`.

## State And Persistence
No state is persisted by this file. Parsed config drives root paths, thin pool names, filesystem creation, and cleanup policy.

## Dependencies And Integration Points
It depends on `go-toml/v2`, Docker units parsing, and filesystem type constants from `snapshotter.go`.

## Risks
`parse` requires `BaseImageSize` to parse before `Validate`, so missing base size can surface as a parse error in some call paths. Unsupported filesystem strings fail validation.

## Test Signals
`config_test.go` covers TOML loading, invalid paths, invalid size parsing, required field errors, and a valid minimal config.
