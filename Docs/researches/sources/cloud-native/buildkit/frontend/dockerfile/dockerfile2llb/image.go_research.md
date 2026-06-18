# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/image.go

Purpose: provides image config helpers for safe mutation during stage inheritance and scratch image initialization.

Important APIs: `clone`, `cloneX`, and `emptyImage`.

Control flow: `clone` shallow-copies the OCI image then deep-copies mutable slices/maps in Docker image config, healthcheck test slice, shell/onbuild, exposed ports, volumes, labels, and history. `cloneX` handles nil pointers. `emptyImage` initializes platform fields, rootfs type, working dir, and non-Windows PATH.

State and persistence: prevents child stages mutating base stage image metadata by aliasing shared maps/slices.

Dependencies and integration: used when resolving base stages and scratch images in `convert.go`; uses system default PATH.

Risks and test signals: omissions in deep copy can leak metadata mutations across stages. `image_test.go` specifically guards mutable field isolation.
