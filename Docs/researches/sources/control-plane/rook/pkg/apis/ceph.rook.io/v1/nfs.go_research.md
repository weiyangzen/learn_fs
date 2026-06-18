# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs.go

Purpose: implements helper behavior for Ceph NFS CRD security and networking fields. It determines whether Kerberos is enabled, supplies the default Kerberos principal, inherits host-network settings from the cluster, and validates NFS SSSD/Kerberos volume-source configuration.

Important APIs/types/functions: `NFSSecuritySpec.KerberosEnabled`, `KerberosSpec.GetPrincipalName`, `CephNFS.IsHostNetwork`, `NFSSecuritySpec.Validate`, and `volSourceExistsAndIsEmpty`. Important referenced types include `SSSDSpec`, `SSSDSidecar`, `AdditionalVolumeMounts`, `ConfigFileVolumeSource`, `KerberosSpec`, `CephNFS`, and `ClusterSpec`.

Control flow: `KerberosEnabled` is nil-safe and returns true only when the `Kerberos` pointer is present. `GetPrincipalName` maps an empty principal to `"nfs"`. `IsHostNetwork` prefers the NFS server-level `HostNetwork` pointer when set, otherwise delegates to `ClusterSpec.Network.IsHost()`. `Validate` is a sequence of guard clauses: nil security is accepted; SSSD requires a runtime sidecar, a sidecar image, any present config volume source to be non-empty, every additional file to have a non-empty unique `SubPath`, and every additional file volume source to be non-empty. Kerberos config/keytab volume sources are similarly rejected when explicitly present but empty.

State and persistence: no state is stored or persisted. Validation is pure aside from reading nested CRD fields and converting Rook volume wrappers to Kubernetes `VolumeSource`.

Dependencies/integration: depends on `github.com/pkg/errors`, `reflect.DeepEqual`, and Kubernetes core `VolumeSource`. Operators call these helpers while reconciling Ceph NFS daemons, sidecars, Kerberos keytabs, and host-network placement.

Risks: `volSourceExistsAndIsEmpty` treats a nil source as absent/allowed but an explicitly empty source as invalid, so defaulting code must preserve that distinction. `Validate` returns on the first error, not an aggregate. `IsHostNetwork` assumes a non-nil cluster spec pointer.

Test signals: paired with `nfs_test.go`, which covers nil/empty security, missing SSSD runtime, missing image, empty explicit volume sources, duplicate additional-file subpaths, Kerberos enablement, and principal defaulting.
