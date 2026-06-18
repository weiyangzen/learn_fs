# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs_test.go

Purpose: tests NFS API helper behavior around SSSD sidecar validation, Kerberos detection, and default Kerberos principal names.

Important APIs/types/functions: exercises `NFSSecuritySpec.Validate`, `NFSSecuritySpec.KerberosEnabled`, and `KerberosSpec.GetPrincipalName`. Test fixtures use `SSSDSpec`, `SSSDSidecar`, `SSSDSidecarConfigFile`, `AdditionalVolumeMounts`, `ConfigFileVolumeSource`, `KerberosSpec`, and Kubernetes `ConfigMapVolumeSource`.

Control flow: `TestNFSSecuritySpec_Validate` builds a table of security specs and desired error outcomes. It wraps SSSD snippets with a local `withSSSD` helper and uses a config-map volume source as a valid non-empty volume. Subtests check nil and empty security, missing SSSD sidecar runtime, empty sidecar, fully specified sidecar, missing image, optional empty config file, explicit empty config volume, empty additional-file list, multiple valid additional files, missing `SubPath`, duplicate `SubPath`, and empty additional-file volume source. Separate subtests verify nil/empty Kerberos state and principal default behavior.

State and persistence: test-only local state; no persistence. It does not touch cluster state or global flags.

Dependencies/integration: depends on testify and Kubernetes core volume types. The tests encode how CRD users can omit optional files while still rejecting explicitly empty `VolumeSource` objects that cannot mount anything.

Risks: one additional-file failure case uses both an empty `SubPath` and empty volume source, so the observed error is driven by validation order rather than isolating only volume-source behavior. The validation table asserts only error presence, not exact messages.

Test signals: good coverage of NFS security validation branches and nil-safety. It does not test `CephNFS.IsHostNetwork`; host-network inheritance for analogous CRDs is mainly signaled by other network tests.
