# sources/cloud-native/nydus/contrib/nydusify/pkg/committer/diff/archive/tar_unix_test.go

Purpose: tests Unix-specific tar helper behavior.

Important APIs and flow: tests validate mode normalization and special header handling for Unix file modes where feasible in a unit-test environment. They complement `tar_test.go` by covering helper branches that are compiled only on Unix.

State and persistence: uses temporary filesystem entries and in-memory headers/buffers. Device node coverage may be constrained by permissions.

Dependencies and integration: verifies the tar writer's platform layer, which is critical for container image fidelity.

Risks and test signals: useful for permission/mode regressions, but privileged device and xattr scenarios may not be fully covered on all CI systems.
