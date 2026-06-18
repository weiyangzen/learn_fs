<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go

## Purpose
This file tests `addSecurityConfigsToPod` and SSSD-specific pod mutations for CephNFS.

## Important APIs and control flow
Test helpers create base CephNFS objects, a mock reconciler with Ceph image/version, and a mock pod with a Ganesha and dbus container. Tests verify nil and empty security specs add nothing. SSSD tests verify generated nsswitch and socket-copy init containers, SSSD sidecar insertion, volume and mount sets, image selection, resource propagation, optional config-map mount behavior, debug-level args, and preservation of pre-existing pod containers and volumes.

## State and persistence
All state is in-memory Kubernetes pod specs. The tests do not create real ConfigMaps, Secrets, or pods.

## Dependencies and integration points
The tests use CephNFS security CRD structs, Kubernetes resource quantities, Rook container spec testers, and helper functions that extract volume, mount, and container names. They validate integration between security helpers and the base pod structure expected from `spec.go`.

## Risks and test signals
Direct tests focus on SSSD; Kerberos-only and SSSD-plus-Kerberos paths are tested at Deployment level in `spec_test.go`. These tests are sensitive to volume names and resource formatting, making them useful for detecting accidental pod-spec drift.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security_test.go -->
