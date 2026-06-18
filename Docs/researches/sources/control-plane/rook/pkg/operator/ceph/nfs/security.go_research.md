<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/security.go

## Purpose
This file augments NFS-Ganesha pod specs with optional SSSD and Kerberos support. It creates init containers, sidecars, volumes, and mounts needed for identity lookup, nsswitch overrides, generated Kerberos config, keytabs, and additional security files.

## Important APIs and control flow
`addSecurityConfigsToPod` checks `nfs.Spec.Security` and dispatches to SSSD and/or Kerberos helpers. `addSSSDConfigsToPod` always adds a generated `/etc/nsswitch.conf` init container and volume for SSSD, then optionally adds an SSSD sidecar, shared sockets/cache volumes, SSSD config file, additional files, and mounts into the Ganesha container. `addKerberosConfigsToPod` adds generated `krb5.conf` resources, mounts optional Kerberos config files and keytab, and updates the Ganesha container. `generateSssdSidecarResources` builds shared emptyDir volumes, optional config/additional-file volumes, SSSD sidecar, socket-copy init container, and extra Kerberos mounts when both features are enabled. `generateKrbConfResources` creates an init container that writes `krb5.conf` and optional `idmapd.conf`.

## State and persistence
Security state is expressed in pod spec volumes, mounts, init containers, and sidecars. Runtime files live in `emptyDir` volumes, ConfigMap/Secret projected volumes, and generated files mounted with `subPath`.

## Dependencies and integration points
The file depends on CephNFS CRD security types, Rook container lookup helpers, generated volume/mount helpers, cluster image settings, and Kubernetes core pod APIs. It integrates with `spec.go` after base containers are assembled.

## Risks and test signals
The helpers mutate container slices returned by `k8sutil.GetContainerByName`; correctness depends on that helper returning a writable reference into the slice. Volume names are fixed, so collisions with future base volumes would be risky. Shell-generated config content includes user-provided domain name without escaping. Tests cover nil/empty security, SSSD with and without config, resource propagation, volume/mount matching, and default pod preservation; Kerberos detail coverage is stronger in `spec_test.go` than in this file's direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/security.go -->
