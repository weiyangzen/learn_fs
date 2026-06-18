
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_test.go -->
# sources/cloud-native/containerd/internal/cri/server/helpers_test.go

## Purpose

This test file covers shared CRI server helper behavior around image user parsing, runtime option generation and decoding, OCI environment deduplication, recursive removal basics, PID namespace target validation, Windows resource projection, and Linux host-network detection.

## Important APIs, Types, and Functions

Tests include `TestGetUserFromImage`, `TestGenerateRuntimeOptions`, `TestEnvDeduplication`, `TestEnsureRemoveAllNotExist`, `TestEnsureRemoveAllWithDir`, `TestEnsureRemoveAllWithFile`, helper `addContainer`, `TestValidateTargetContainer`, `TestGetRuntimeOptions`, `TestCopyResourcesToStatusWindowsAffinity`, and `TestHostNetwork`.

## Control Flow

The tests are table-driven. Runtime options are generated from TOML configs and compared to runc option structs. Env deduplication uses `oci.WithEnv` repeatedly to verify later values replace earlier values without reordering unaffected keys. Target-container validation builds fake containers with running, stopped, missing, and cross-sandbox conditions. Host networking is skipped unless running on Linux.

## State and Persistence Behavior

The tests use temporary files/directories and in-memory fake CRI stores. Runtime option tests decode configuration into memory only. No real containerd runtime tasks are created.

## Dependencies and Integration Points

Dependencies include CRI runtime API, containerd CRI config, container store, OCI helper package, runc options, TOML decoding, typeurl, and test assertion libraries. The tests protect helper behavior used by container creation, sandbox setup, resource status reporting, and runtime configuration handling.

## Risks and Edge Cases

Coverage is broad but shallow for several helpers. SELinux label parsing, cgroup path construction, user namespace parsing, CRI event generation, and image reference conversion are not covered here. Host network coverage is Linux-only in this file; Windows has a separate test file.

## Test Signals

Passing tests confirm user/group truncation, numeric UID detection, nil and typed-nil runtime options, environment override semantics, safe basic removal, PID namespace target validation, Windows CPU affinity copy, and Linux namespace-mode host network detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/helpers_test.go -->
