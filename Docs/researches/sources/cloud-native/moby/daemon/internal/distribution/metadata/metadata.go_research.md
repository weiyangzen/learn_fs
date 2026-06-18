# sources/cloud-native/moby/daemon/internal/distribution/metadata/metadata.go

## Purpose
Provides a filesystem-backed key/value store for distribution metadata.

## APIs, Control Flow, and Integration
`Store` exposes `Get`, `Set`, and `Delete` by namespace/key. `FSMetadataStore` creates the base path, protects operations with an RW mutex, maps namespace/key to nested paths, reads files, atomically writes values after creating parent directories, and removes files.

## State, Dependencies, and Risks
Persistence is under the configured base path with namespace directories and key paths, using 0700 base, 0755 namespace dirs, and 0644 files. Risks include unsanitized keys creating nested paths, delete errors for missing files, and process-local locking only. It is used by v2 metadata service for layer digest/diffID mappings.
