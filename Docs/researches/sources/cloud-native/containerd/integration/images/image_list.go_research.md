# sources/cloud-native/containerd/integration/images/image_list.go

## Purpose

This package centralizes public image references used by containerd integration tests and allows overriding them from a TOML file. It provides stable integer constants and a `Get` accessor for test code.

## Important APIs, Types, And Functions

- `imageListFile` defines the `-image-list` flag.
- `ImageList` contains named image reference fields.
- `initImages` sets defaults, optionally loads TOML overrides, logs the list, and initializes `imageMap`.
- Constants `Alpine`, `BusyBox`, `Pause`, `ResourceConsumer`, `VolumeCopyUp`, `VolumeOwnership`, `ArgsEscaped`, `Nginx`, and `Whiteout` index the map.
- `Get` lazily initializes once and returns a reference by constant.

## Control Flow

The first `Get` call triggers `initOnce.Do`. Defaults are assigned, optional TOML content is read and unmarshaled over the struct, and `initImageMap` maps constants to struct fields. Later calls reuse the initialized map.

## State And Persistence Behavior

Package-level `imageList`, `imageMap`, and `initOnce` hold process-local state. No files are written. The TOML override file is read once and later changes are ignored.

## Dependencies And Integration Points

It integrates with Go flags parsed in test startup, containerd logging, and `pelletier/go-toml/v2`. Almost every integration test imports this package for image references.

## Risks And Edge Cases

Unknown integer constants return the zero map value. TOML key casing must match decoder behavior; the sample mixes lower-case and exported field names. Read/unmarshal failures panic because tests cannot proceed safely with an invalid image list.

## Test Signals

Indirect test signal is broad: successful image pulls across the integration suite validate that defaults or overrides are valid.
