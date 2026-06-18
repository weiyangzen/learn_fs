## sources/distributed-fs/juicefs/pkg/chunk/utils_unix_test.go

Purpose: tests Unix root-volume detection helper.

Important tests: `TestInRootVolume` checks expected behavior for temporary/current/root-like paths by calling `inRootVolume`.

State and persistence: no persistent mutation; reads filesystem metadata.

Dependencies and integration points: depends on local filesystem device layout, so expectations may vary in containers or unusual mount configurations.

Risks and test signals: useful for cache free-ratio safety logic but potentially environment-sensitive if test assumptions about mounts do not hold.
