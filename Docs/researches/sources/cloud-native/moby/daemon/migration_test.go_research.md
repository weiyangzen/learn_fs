# sources/cloud-native/moby/daemon/migration_test.go

## Purpose
This file tests container platform migration logic using a mock platform reader.

## Important APIs, Types, And Functions
`mockPlatformReader` implements `ReadPlatformFromImage` and `ReadPlatformFromConfigByImageManifest`, mapping synthetic image IDs/digests to platforms or errors. `TestContainerMigrateOS` invokes `migrateContainerOS` for table-driven cases.

## Control Flow
Each case creates a container with combinations of deprecated `OS`, `ImageID`, and `ImageManifest`. The migration is run and `ctr.ImagePlatform` is compared to the expected platform.

## State, Persistence, And Dependencies
Only local container structs are mutated. Dependencies include `container.Container`, internal `image.ID`, OCI platform types, containerd platform defaults, and gotest assertions.

## Integration Points
The test captures migration compatibility across graphdriver and containerd image stores, including malformed/missing platform paths.

## Risks And Edge Cases
The mock abstracts away actual manifest JSON/content-store behavior, so it tests decision order rather than blob parsing. The test intentionally tolerates fallback to host default for a multi-platform image ID.

## Test Signals
Coverage includes pre-OS fallback, successful platform reads, missing images preserving OS-only information, ImageManifest priority, and fallback from missing manifest to image lookup.
