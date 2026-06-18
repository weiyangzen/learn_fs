## sources/cloud-native/moby/daemon/internal/layer/layer_unix.go

Purpose: Provides Unix-like mount ID generation for writable layers.

Important API: `(*layerStore).mountID(name string) string` returns `stringid.GenerateRandomID()`.

Control flow and state: Build-tagged for Linux, FreeBSD, Darwin, and OpenBSD. It ignores the caller-visible mount name and generates a random graphdriver ID.

Dependencies and integration: Used by `CreateRWLayer` in `layer_store.go`. Separates user-visible mount names from graphdriver cache IDs on Unix-like platforms.

Risks: Random ID generation must avoid collisions; collision handling is delegated to graphdriver create errors. Windows differs by using the name directly.

Tests: Indirectly covered by layer and mount tests on Unix-like platforms.
