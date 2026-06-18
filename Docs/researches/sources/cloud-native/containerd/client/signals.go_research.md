# Research: sources/cloud-native/containerd/client/signals.go

## Purpose
Resolves container stop signals from container labels or OCI image config, providing a normalized helper for shutdown behavior.

## Important APIs, Control Flow, And State
`StopSignalLabel` names the containerd label `io.containerd.image.config.stop-signal`. `GetStopSignal` reads container labels and parses the label value with `moby/sys/signal`, falling back to a supplied default signal. `GetOCIStopSignal` validates the default string, reads the image config descriptor, verifies it is a known config media type, reads the config blob, unmarshals `v1.Image`, and returns `Config.StopSignal` or the default. There is no persistent mutation; the functions read labels and content blobs.

## Dependencies And Integration
Uses client `Container` and `Image` interfaces, content reads, image media type helpers, OCI image spec JSON, and signal parsing. It integrates with stop/kill workflows that need image-authored stop signal semantics.

## Risks And Test Signals
Risks include invalid signal strings, unknown config media types, malformed config blobs, and label values overriding defaults unexpectedly. Tests should cover missing labels/config signals, invalid defaults, named and numeric signals, config media validation, and content read/unmarshal errors.
