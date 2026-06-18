# subset-b-000440 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network_test.go

Purpose: unit-tests the Ceph `NetworkSpec` compatibility, validation, host-network interpretation, address-range validation, and Multus network-selection serialization behavior. It is a test-only file for API helper behavior defined in the same `v1` package.

Important APIs/types/functions: tests cover `NetworkSpec`, `NetworkProviderDefault`, `NetworkProviderHost`, `NetworkProviderMultus`, `ValidateNetworkSpec`, `NetworkSpec.IsHost`, `SetEnforceHostNetwork`, `AddressRangesSpec.IsEmpty`, `AddressRangesSpec.Validate`, `NetworkSpec.GetNetworkSelection`, and `NetworkSelectionsToAnnotationValue`. It also exercises `CIDR`, `CephNetworkPublic`, `CephNetworkCluster`, and the network-attachment-definition client `NetworkSelectionElement`.

Control flow: YAML snippets are converted to JSON and unmarshaled into API structs to verify CRD wire compatibility. Validation tests build small `NetworkSpec` instances and assert which provider/host-network combinations are rejected. Host-network tests toggle the package-global enforce flag and combine provider values with legacy `HostNetwork`. The address range table validates IPv4, IPv6, IPv4-embedded IPv6, and malformed CIDR inputs. The Multus table calls `GetNetworkSelection` for requested Ceph network types, collects selection objects and errors, and then serializes all selections through `NetworkSelectionsToAnnotationValue`.

State and persistence: the file has no persistence. It mutates only local test objects plus the global host-network enforcement setting via `SetEnforceHostNetwork`, resetting it between scenarios to avoid cross-test leakage.

Dependencies/integration: depends on Go JSON unmarshalling, Kubernetes YAML conversion, testify assertions, and `k8snetworkplumbingwg/network-attachment-definition-client` types. These tests protect the API contract used by operators that translate `NetworkSpec` to pod host networking or Multus annotations.

Risks: tests touch a package-level enforcement flag, so parallelization would need care. The annotation tests compare exact compact JSON strings, making output ordering part of the contract. The suite intentionally tests only a subset of CIDR possibilities because validation is expected to delegate to Go stdlib parsing.

Test signals: strong coverage for legacy `hostNetwork`, provider conflict validation, enforced host-network override, invalid provider fallback, empty/non-empty address ranges, aggregated invalid CIDR counts, JSON and non-JSON Multus inputs, mixed selector forms, unknown selector keys, legacy single-object JSON, and invalid selector parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs.go

Purpose: implements helper behavior for Ceph NFS CRD security and networking fields. It determines whether Kerberos is enabled, supplies the default Kerberos principal, inherits host-network settings from the cluster, and validates NFS SSSD/Kerberos volume-source configuration.

Important APIs/types/functions: `NFSSecuritySpec.KerberosEnabled`, `KerberosSpec.GetPrincipalName`, `CephNFS.IsHostNetwork`, `NFSSecuritySpec.Validate`, and `volSourceExistsAndIsEmpty`. Important referenced types include `SSSDSpec`, `SSSDSidecar`, `AdditionalVolumeMounts`, `ConfigFileVolumeSource`, `KerberosSpec`, `CephNFS`, and `ClusterSpec`.

Control flow: `KerberosEnabled` is nil-safe and returns true only when the `Kerberos` pointer is present. `GetPrincipalName` maps an empty principal to `"nfs"`. `IsHostNetwork` prefers the NFS server-level `HostNetwork` pointer when set, otherwise delegates to `ClusterSpec.Network.IsHost()`. `Validate` is a sequence of guard clauses: nil security is accepted; SSSD requires a runtime sidecar, a sidecar image, any present config volume source to be non-empty, every additional file to have a non-empty unique `SubPath`, and every additional file volume source to be non-empty. Kerberos config/keytab volume sources are similarly rejected when explicitly present but empty.

State and persistence: no state is stored or persisted. Validation is pure aside from reading nested CRD fields and converting Rook volume wrappers to Kubernetes `VolumeSource`.

Dependencies/integration: depends on `github.com/pkg/errors`, `reflect.DeepEqual`, and Kubernetes core `VolumeSource`. Operators call these helpers while reconciling Ceph NFS daemons, sidecars, Kerberos keytabs, and host-network placement.

Risks: `volSourceExistsAndIsEmpty` treats a nil source as absent/allowed but an explicitly empty source as invalid, so defaulting code must preserve that distinction. `Validate` returns on the first error, not an aggregate. `IsHostNetwork` assumes a non-nil cluster spec pointer.

Test signals: paired with `nfs_test.go`, which covers nil/empty security, missing SSSD runtime, missing image, empty explicit volume sources, duplicate additional-file subpaths, Kerberos enablement, and principal defaulting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs_test.go

Purpose: tests NFS API helper behavior around SSSD sidecar validation, Kerberos detection, and default Kerberos principal names.

Important APIs/types/functions: exercises `NFSSecuritySpec.Validate`, `NFSSecuritySpec.KerberosEnabled`, and `KerberosSpec.GetPrincipalName`. Test fixtures use `SSSDSpec`, `SSSDSidecar`, `SSSDSidecarConfigFile`, `AdditionalVolumeMounts`, `ConfigFileVolumeSource`, `KerberosSpec`, and Kubernetes `ConfigMapVolumeSource`.

Control flow: `TestNFSSecuritySpec_Validate` builds a table of security specs and desired error outcomes. It wraps SSSD snippets with a local `withSSSD` helper and uses a config-map volume source as a valid non-empty volume. Subtests check nil and empty security, missing SSSD sidecar runtime, empty sidecar, fully specified sidecar, missing image, optional empty config file, explicit empty config volume, empty additional-file list, multiple valid additional files, missing `SubPath`, duplicate `SubPath`, and empty additional-file volume source. Separate subtests verify nil/empty Kerberos state and principal default behavior.

State and persistence: test-only local state; no persistence. It does not touch cluster state or global flags.

Dependencies/integration: depends on testify and Kubernetes core volume types. The tests encode how CRD users can omit optional files while still rejecting explicitly empty `VolumeSource` objects that cannot mount anything.

Risks: one additional-file failure case uses both an empty `SubPath` and empty volume source, so the observed error is driven by validation order rather than isolating only volume-source behavior. The validation table asserts only error presence, not exact messages.

Test signals: good coverage of NFS security validation branches and nil-safety. It does not test `CephNFS.IsHostNetwork`; host-network inheritance for analogous CRDs is mainly signaled by other network tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nvmeof.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nvmeof.go

Purpose: provides the host-network helper for the Ceph NVMe-oF gateway CRD.

Important APIs/types/functions: `CephNVMeOFGateway.IsHostNetwork` reads `n.Spec.HostNetwork` and falls back to `ClusterSpec.Network.IsHost()`.

Control flow: the method is a simple precedence check. An explicitly set gateway `HostNetwork` pointer wins, preserving both true and false. When the field is nil, the gateway inherits the cluster network policy.

State and persistence: no mutable state or persistence. The method interprets CRD fields only.

Dependencies/integration: depends on `CephNVMeOFGateway`, `ClusterSpec`, and the network helper implementation in the same API package. The operator can use it to decide whether gateway pods should use Kubernetes host networking.

Risks: nil receiver or nil cluster pointer would panic; callers are expected to pass real API objects. There is no local test file in this subset, so behavior is inferred from the identical NFS/object host-network helper pattern and network tests.

Test signals: no direct tests in this item. Regression coverage should include explicit true, explicit false, and nil inheritance from cluster network provider/legacy host-network settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nvmeof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object.go

Purpose: implements object-store helper and validation logic for Ceph RGW CRDs, including multisite/external/TLS detection, port selection, host-network inheritance, object-store spec validation, TLS cipher validation, service naming, advertised endpoint calculation, status-condition accessors, and endpoint address stringification.

Important APIs/types/functions: `ServiceServingCertKey`, `objectStoreNameMaxLen`, `ObjectStoreSpec.IsMultisite`, `IsTLSEnabled`, `IsRGWDashboardEnabled`, `GetPort`, `IsExternal`, `IsHostNetwork`, `ObjectRealmSpec.IsPullRealm`, `ValidateObjectSpec`, `validateObjectStoreSecurity`, `isTLSv1_2orBelowEnabled`, `GetServiceServingCert`, `CephObjectStore.GetServiceName`, `GetServiceDomainName`, `AdvertiseEndpointIsSet`, `GetAdvertiseEndpoint`, `GetAdvertiseEndpointUrl`, `CephObjectStore.GetStatusConditions`, `CephObjectZone.GetStatusConditions`, and `EndpointAddress.String`.

Control flow: object-store validation first requires metadata name and namespace, then enforces the 38-character internal-store name limit only for non-external stores. It validates secure port range and requires at least one usable port. Hosting validation checks optional advertise endpoint DNS and port bounds, and validates all hosting DNS names with Kubernetes DNS-1123 rules while preserving the offending names in the error. Security validation allows TLS 1.3 cipher suites independently but requires at least one TLS 1.2-or-below option when legacy `Ciphers` are set. Advertise endpoint calculation starts from the internal service domain, uses the first external endpoint for external stores, and finally lets `hosting.advertiseEndpoint` override address, port, and TLS. URL formatting uses `net.JoinHostPort`, preserving IPv6 bracket handling.

State and persistence: no persistence. Status helpers return pointers to in-memory condition slices so shared status utilities can mutate CRD status. Helper methods otherwise derive values from object fields.

Dependencies/integration: depends on `fmt`, `net`, `github.com/pkg/errors`, Kubernetes `validation.IsDNS1123Subdomain`, and `k8s.io/utils/ptr`. It integrates with the RGW operator, OpenShift service-serving certificate annotations, Ceph dashboard expectations, multisite realm/zone logic, and bucket-topic/notification components that need stable endpoint URLs.

Risks: `IsTLSEnabled` requires a non-zero secure port plus either user cert ref or service-serving cert annotation; secure port alone is treated as non-TLS for helper decisions. `GetServiceServingCert` indexes `Gateway.Service.Annotations` without checking whether the map is nil, which is safe for reads but returns empty. `AdvertiseEndpointIsSet` requires both DNS and port, so partial overrides are ignored here but rejected by full spec validation. `GetAdvertiseEndpoint` chooses the first external endpoint only. Name-length validation is skipped for external stores for compatibility.

Test signals: `object_test.go` covers required name/namespace, port and secure-port validation, hosting DNS and advertised port validation, TLS cipher/security rules, TLS enablement, internal/external advertise URL generation for IPv4, IPv6, and hostnames, nil hosting, DNSNames non-effect, explicit HTTP/HTTPS advertise endpoint overrides, and missing-port error paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object_test.go

Purpose: validates Ceph object-store API helper behavior, especially object-store validation, TLS enablement, security cipher constraints, and advertised endpoint URL selection.

Important APIs/types/functions: tests `ValidateObjectSpec`, `validateObjectStoreSecurity`, `ObjectStoreSpec.IsTLSEnabled`, and `CephObjectStore.GetAdvertiseEndpointUrl`. Fixtures use `CephObjectStore`, `ObjectStoreSpec`, `GatewaySpec`, `ObjectStoreHostingSpec`, `ObjectEndpointSpec`, `ObjectStoreSecuritySpec`, `SslOptionsSpec`, `EndpointAddress`, `RGWServiceSpec`, `Annotations`, and `ServiceServingCertKey`.

Control flow: the validation test starts from a minimal valid store, mutates gateway ports and object metadata to trigger errors, then runs hosting subtests for invalid wildcard/empty advertise DNS, port 0, port 65536, and invalid hosting DNS names with assertions that valid names are not incorrectly reported. Security subtests verify TLS 1.3 cipher suites are allowed, legacy ciphers fail when all TLS 1.2-or-below options are disabled, then pass when TLS 1.2 is enabled, and that ciphers and cipher suites can coexist. TLS enablement subtests combine secure ports, certificate refs, and OpenShift service-serving cert annotations. The advertise URL table builds internal stores, external IPv4/IPv6/hostname stores, nil hosting, nil advertise endpoint, HTTP override, HTTPS override, cert removal, and missing port cases.

State and persistence: test-only local state. The advertise URL table mutates copied CRD structs via helper closures; no Kubernetes API or persistent state is touched.

Dependencies/integration: uses testify and Kubernetes `metav1`. The tests freeze stable behavior for service-domain naming, external endpoint precedence, IPv6 URL formatting, and OpenShift certificate-driven TLS.

Risks: several helper closures mutate the object they receive; table entries are built eagerly, so reuse must be understood before extending tests. `GetAdvertiseEndpointUrl` tests assume only the first external endpoint is used. Error checks usually look for substrings, not full error values.

Test signals: broad branch coverage for object-store validation and URL behavior. It does not directly test `IsMultisite`, `IsRGWDashboardEnabled`, `IsHostNetwork`, `ObjectRealmSpec.IsPullRealm`, status-condition accessors, or `EndpointAddress.String` outside its use in advertise endpoint selection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement.go

Purpose: provides placement merging and application helpers that map Rook `PlacementSpec` CRD fields into Kubernetes `PodSpec` scheduling fields for Ceph daemons.

Important APIs/types/functions: `PlacementSpec.All`, `Placement.ApplyToPodSpec`, `Placement.mergeNodeAffinity`, `Placement.mergeTolerations`, `Placement.Merge`, `GetMgrPlacement`, `GetMonPlacement`, `GetArbiterPlacement`, and `GetOSDPlacement`.

Control flow: `ApplyToPodSpec` ensures `PodSpec.Affinity` exists, then applies placement fields. Node affinity is merged with any existing pod node affinity; pod affinity and anti-affinity are deep-copied and overwrite existing values; tolerations are prepended/merged; topology spread constraints replace the pod's existing constraints. `mergeNodeAffinity` starts from a deep copy of placement affinity, appends preferred terms from existing and placement affinities, and for required node selectors merges only the first selector term's match expressions and fields when both sides have required terms. `Merge` overlays a more specific placement onto a base placement, with specific affinity and topology fields replacing base fields and tolerations merged. Daemon-specific getters merge `all` with mgr, mon, or osd placement; arbiter deliberately returns only the arbiter placement without `all`.

State and persistence: no persistence. Methods return or mutate in-memory Kubernetes scheduling structs. `ApplyToPodSpec` mutates the provided pod spec.

Dependencies/integration: depends on Kubernetes core `v1` scheduling types. This logic is used by Rook reconcilers when creating deployments, jobs, daemonsets, and pods for Ceph components.

Risks: required node affinity merging only considers the first `NodeSelectorTerm`, which cannot represent all Kubernetes OR/AND combinations. `mergeTolerations` appends existing tolerations after placement tolerations without deduplication. `ApplyToPodSpec` assigns topology spread constraints directly rather than deep-copying. `Merge` starts with a shallow copy, so pointer fields may alias original placement structs.

Test signals: `placement_test.go` covers YAML unmarshalling, node-affinity merge variants, pod-spec application, deep copy of anti-affinity, toleration ordering, topology replacement, and daemon-independent merge behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement_test.go

Purpose: tests Kubernetes scheduling placement parsing, merging, and application behavior for Rook Ceph API placement helpers.

Important APIs/types/functions: exercises `Placement`, `PlacementSpec`, `Placement.ApplyToPodSpec`, `Placement.mergeNodeAffinity`, `Placement.Merge`, `Placement.mergeTolerations`, and helper fixtures `placementTestGetTolerations`, `placementTestGetTopologySpreadConstraints`, `placementAntiAffinity`, and `placementTestGenerateNodeAffinity`.

Control flow: `TestPlacementSpec` converts YAML to JSON and verifies a typed `Placement` with node affinity, tolerations, and topology spread constraints. `TestMergeNodeAffinity` covers nil existing affinity, existing preferred affinity without required selector, and merging required selector expressions. `TestPlacementApplyToPodSpec` applies full and partial placements to pod specs, verifies topology replacement, preferred-affinity merging, anti-affinity deep copy behavior, and toleration append order. `TestPlacementMerge` covers overlaying tolerations, node affinity, and topology constraints. `TestMergeToleration` validates nil and non-nil toleration merging.

State and persistence: test-only local scheduling structs; no persistence or external Kubernetes API calls.

Dependencies/integration: depends on testify, Kubernetes core `v1`, `metav1.LabelSelector`, and Kubernetes YAML conversion. Tests protect the scheduling contract used by multiple Rook Ceph daemons.

Risks: expected values encode current merge limitations, such as first-term required affinity merging and no toleration deduplication. Tests check anti-affinity deep-copy behavior but do not similarly protect topology spread constraints from aliasing.

Test signals: strong coverage for placement helper edge cases and merge order. Daemon-specific getter functions are not directly tested in this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/placement_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool.go

Purpose: implements Ceph block pool helper methods and validation for replicated, erasure-coded, hybrid, named, and mirrored pool specs.

Important APIs/types/functions: `PoolSpec.IsReplicated`, `PoolSpec.IsErasureCoded`, `PoolSpec.IsHybridStoragePool`, `ValidateCephBlockPool`, `validatePoolSpec`, `CephBlockPool.ToNamedPoolSpec`, `CephBlockPool.GetStatusConditions`, `CephBlockPoolRadosNamespace.GetStatusConditions`, and `MirroringSpec.SnapshotSchedulesEnabled`.

Control flow: pool kind helpers inspect replicated size, erasure-coded data/coding chunks, and hybrid-storage pointer presence. `ValidateCephBlockPool` rejects erasure coding for Ceph built-in pools `.rgw.root`, `.mgr`, and `.nfs`, then delegates to generic named-pool validation. `validatePoolSpec` requires either erasure-coded or replicated configuration, rejects simultaneous erasure-coded and replicated settings, and enforces minimum data/coding chunks when replication is not selected. `ToNamedPoolSpec` uses `spec.name` when provided or falls back to the Kubernetes CR name. Snapshot scheduling is considered enabled whenever the schedule list is non-empty.

State and persistence: no persistence. Status accessors return condition-slice pointers for status update helpers. Validation reads only CRD fields.

Dependencies/integration: depends on `github.com/pkg/errors`. Reconciler code uses this to reject invalid pool CRs and to produce normalized `NamedPoolSpec` input for Ceph pool creation.

Risks: `SnapshotSchedulesEnabled` ignores `MirroringSpec.Enabled` and mode; schedule presence alone controls the result. Erasure-coded detection includes `Algorithm` during validation conflict checks, but `IsErasureCoded` only checks chunk fields. `ToNamedPoolSpec` allows `Spec.Name` to override resource identity, which consumers must handle carefully.

Test signals: `pool_test.go` covers missing replication/EC configuration, replicated success, EC success, simultaneous EC/replicated rejection, and snapshot-schedule presence behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool_test.go

Purpose: unit-tests pool validation and mirroring snapshot-schedule helper behavior.

Important APIs/types/functions: tests `validatePoolSpec`, `CephBlockPool.ToNamedPoolSpec`, and `MirroringSpec.SnapshotSchedulesEnabled` using `CephBlockPool`, `PoolSpec`, `ReplicatedSpec`, `ErasureCodedSpec`, and `SnapshotScheduleSpec`.

Control flow: `TestValidatePoolSpec` mutates one `CephBlockPool` through invalid empty configuration, valid replicated size, valid erasure-coded chunks, and invalid simultaneous replicated/erasure-coded configuration, delegating through `ToNamedPoolSpec`. `TestMirroringSpec_SnapshotSchedulesEnabled` table-checks disabled and enabled schedule-list cases.

State and persistence: test-only local CRD structs; no persistence.

Dependencies/integration: uses testify assertions and standard testing. It protects validation used before Ceph pool reconciliation.

Risks: the mirroring test case named `"disabled"` sets `Enabled: true` but an empty schedule list, documenting that helper behavior ignores the enabled flag. Tests do not cover built-in pool erasure-coding rejection, target-size-ratio-only replicated pools, minimum EC data/coding chunk failures, hybrid storage, status condition accessors, or name override fallback.

Test signals: basic positive/negative validation coverage with focused schedule-list behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses.go

Purpose: provides lookup helpers for daemon-specific Kubernetes priority class names stored in a Rook `PriorityClassNamesSpec` map.

Important APIs/types/functions: `PriorityClassNamesSpec.All`, `GetMgrPriorityClassName`, `GetMonPriorityClassName`, `GetOSDPriorityClassName`, `GetCleanupPriorityClassName`, `GetCrashCollectorPriorityClassName`, and `GetCephExporterPriorityClassName`. Key constants such as `KeyAll`, `KeyMgr`, `KeyMon`, `KeyOSD`, `KeyCleanup`, `KeyCrashCollector`, and `KeyCephExporter` are defined elsewhere in the package.

Control flow: `All` returns the class configured for `all`, or empty string. Every daemon-specific getter checks whether its daemon key exists; if not, it falls back to `All`; if it exists, it returns the daemon-specific value, including an explicit empty string.

State and persistence: no persistence or mutation. The map is read-only from these helpers.

Dependencies/integration: no external imports. Reconciler code uses these helpers to populate pod specs for Ceph manager, monitor, OSD, cleanup, crashcollector, and exporter workloads.

Risks: explicit empty daemon entries suppress fallback to `all`. There are no helpers here for every resource key in `resources.go`, so missing daemon types require separate handling. Map lookup on a nil map is safe and returns empty fallback.

Test signals: `priorityclasses_test.go` verifies YAML unmarshalling and `All` fallback behavior. Daemon-specific getter fallback/override behavior is not exhaustively tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses_test.go

Purpose: tests priority-class map unmarshalling and default `all` lookup behavior.

Important APIs/types/functions: exercises `PriorityClassNamesSpec` JSON/YAML unmarshalling and `PriorityClassNamesSpec.All`.

Control flow: `TestPriorityClassNamesSpec` converts YAML with `all`, `mgr`, `mon`, `osd`, and `crashcollector` entries into JSON, unmarshals into `PriorityClassNamesSpec`, and compares the resulting map. `TestPriorityClassNamesDefaultToAll` constructs a map with `all` and `mon` entries and asserts that `All` returns the global class.

State and persistence: test-only local maps; no persistence.

Dependencies/integration: depends on testify and Kubernetes YAML conversion. It protects the CRD map shape used by cluster specs.

Risks: despite its name, `TestPriorityClassNamesDefaultToAll` only tests `All()`, not daemon-specific fallback to `all`. It does not cover explicit empty daemon-specific entries, cleanup/exporter getters, or nil maps.

Test signals: confirms YAML keys map into the expected `PriorityClassNamesSpec` and that the global `all` key can be read.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/register.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/register.go

Purpose: registers manually written Rook Ceph v1 API types with a Kubernetes runtime scheme and provides the group/version/resource helpers for this API package.

Important APIs/types/functions: `CustomResourceGroup`, `Version`, `SchemeGroupVersion`, `Resource`, `SchemeBuilder`, `localSchemeBuilder`, `AddToScheme`, `init`, and `addKnownTypes`.

Control flow: package initialization registers `addKnownTypes` with the local scheme builder. `addKnownTypes` calls `scheme.AddKnownTypes` for the Ceph group/version and includes core Rook Ceph CRDs such as cluster, client, block pool, filesystem, NFS, NVMe-oF gateway, object store/user/account/realm/zone group/zone, bucket topic/notification, mirrors, subvolume groups, pool namespaces, and COSI driver types. It then adds the group version to the scheme. The same function also registers lib-bucket-provisioner `ObjectBucketClaim` and `ObjectBucket` types under their own scheme group version.

State and persistence: no durable persistence. It mutates the provided in-memory `runtime.Scheme` and sets up package-level scheme-builder registration.

Dependencies/integration: depends on Kubernetes `metav1`, `runtime`, and `schema`, the parent `ceph.rook.io` API package for the group name, and `github.com/kube-object-storage/lib-bucket-provisioner` v1alpha1 types. This is a core integration point for Kubernetes clients, controllers, informers, serializers, and tests that need typed scheme registration.

Risks: new CRD types must be added here or clients using only manual registration may fail to encode/decode them. The comment notes generated registration happens elsewhere, so builds without generated files rely on this file. `CustomResourceGroup` duplicates the string while `SchemeGroupVersion` uses the parent package constant; drift would be confusing even though current values match.

Test signals: no direct tests in this subset. Runtime scheme smoke tests should verify `AddToScheme` registers every expected CRD and the bucket-provisioner types.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/resources.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/resources.go

Purpose: defines resource-spec map keys and lookup helpers for Kubernetes resource requirements of Ceph daemon pods, sidecars, and jobs.

Important APIs/types/functions: constants `ResourcesKeyMon`, `ResourcesKeyMgr`, `ResourcesKeyMgrSidecar`, `ResourcesKeyOSD`, `ResourcesKeyPrepareOSD`, `ResourcesKeyCmdReporter`, `ResourcesKeyMDS`, `ResourcesKeyCrashCollector`, `ResourcesKeyLogCollector`, `ResourcesKeyRBDMirror`, `ResourcesKeyFilesystemMirror`, `ResourcesKeyCleanup`, `ResourcesKeyCephExporter`, and `ResourcesKeyFloatingMonShutDownApp`. Helper functions include `GetMgrResources`, `GetMgrSidecarResources`, `GetMonResources`, `GetOSDResources`, `GetOSDResourcesForDeviceClass`, `getOSDResourceKeyForDeviceClass`, `GetPrepareOSDResources`, `GetCmdReporterResources`, `GetCrashCollectorResources`, `GetLogCollectorResources`, `GetFloatingMonShutDownAppResources`, `GetCleanupResources`, and `GetCephExporterResources`.

Control flow: most helpers are direct map lookups on `ResourceSpec`. OSD lookup has special logic: no device class returns the common `osd` resources; a device class first checks `osd-<class>`, then falls back to common `osd`. `GetOSDResourcesForDeviceClass` reports whether a class-specific key exists and returns an empty `ResourceRequirements` plus false when absent.

State and persistence: no persistence or mutation. Map reads on nil or missing keys yield zero-value Kubernetes resource requirements.

Dependencies/integration: depends on Kubernetes core `v1.ResourceRequirements`. Controllers use this file to consistently map CRD resource configuration onto pod containers and jobs.

Risks: several constants do not have corresponding getters in this file (`mds`, `rbdmirror`, `fsmirror`), implying other code may index them directly. Device-class keys are dynamically generated with a simple `osd-` prefix; class names containing unexpected characters still produce map keys. Missing keys silently become zero resource requests/limits.

Test signals: no direct tests in this subset. Useful tests would cover OSD device-class fallback, explicit class-specific retrieval, nil map behavior, and all daemon key constants used by reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/resources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc.go

Purpose: constructs an OpenShift `SecurityContextConstraints` object suitable for Rook-Ceph service accounts.

Important APIs/types/functions: `NewSecurityContextConstraints(name string, namespaces ...string) *secv1.SecurityContextConstraints`.

Control flow: the function returns a fully populated SCC with OpenShift API metadata, privileged containers enabled, hostPath volumes enabled, host IPC enabled, host networking and host ports disabled, allowed capabilities `MKNOD` and `SYS_ADMIN`, all capabilities dropped by default, permissive run-as-user and supplemental-group strategies, constrained SELinux and FSGroup strategies, and a fixed set of allowed volume types. It builds the `Users` slice by appending service-account subjects for every namespace: `rook-ceph-system`, `rook-ceph-default`, `rook-ceph-mgr`, `rook-ceph-osd`, `rook-ceph-rgw`, and `rook-ceph-nvmeof`.

State and persistence: no persistence. The returned SCC object is in-memory and can be submitted by callers to the Kubernetes/OpenShift API.

Dependencies/integration: depends on `github.com/openshift/api/security/v1`, Kubernetes core capabilities, and `metav1`. It is an OpenShift-specific integration point for running Rook Ceph components that need privileged storage access.

Risks: the SCC grants broad privileges, including privileged containers and hostPath. Host networking is false here, so workloads requiring host networking must be handled elsewhere. New Rook service accounts need to be added to the hard-coded user list. Namespace argument order controls user ordering.

Test signals: `scc_test.go` only confirms the SCC name and `AllowPrivilegedContainer`; broader security fields and generated users are not tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc_test.go

Purpose: smoke-tests the OpenShift SCC constructor for Rook-Ceph.

Important APIs/types/functions: exercises `NewSecurityContextConstraints`.

Control flow: the single test constructs an SCC with name `"rook-ceph"` and one namespace argument, then asserts that privileged containers are allowed and the object name matches the input.

State and persistence: no persistence; local SCC object only.

Dependencies/integration: depends on testify. The test is a minimal guard for the OpenShift SCC helper used by deployment/install code.

Risks: coverage is shallow. It does not assert API version/kind, volume types, capabilities, host settings, SELinux/FSGroup strategies, or generated service-account users, so security-sensitive regressions could pass.

Test signals: only verifies constructor returns a named privileged SCC.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/scc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security.go

Purpose: provides helper predicates for `KeyManagementServiceSpec`, especially Vault, Azure, IBM Key Protect, KMIP, token, Kubernetes, agent, and TLS configuration detection.

Important APIs/types/functions: `VaultTLSConnectionDetails`, `KeyManagementServiceSpec.IsEnabled`, `IsTokenAuthEnabled`, `IsK8sAuthEnabled`, `IsAgentAuthEnabled`, `IsVaultKMS`, `IsAzureMS`, `IsIBMKeyProtectKMS`, `IsKMIPKMS`, `IsTLSEnabled`, and `getParam`.

Control flow: `IsEnabled` checks whether any connection details exist. Token auth is enabled by a non-empty token secret name. Kubernetes auth is enabled when `VAULT_AUTH_METHOD` equals the Vault library's Kubernetes value and no token secret is configured. Agent auth is enabled when that auth method equals `"agent"` and no token secret is configured. Provider helpers inspect `KMS_PROVIDER` against provider constants or literal provider names. TLS detection scans the Vault CA cert, client cert, and client key environment option names and returns true on the first non-empty configured value. `getParam` trims whitespace from non-empty map values.

State and persistence: no persistence or mutation. Helpers read the CRD's `ConnectionDetails` map and token field.

Dependencies/integration: depends on HashiCorp Vault API env-var constants, libopenstorage secrets provider constants, and Vault auth-method constants. Ceph encryption and KMS integration code uses these predicates to select authentication and provider setup paths.

Risks: methods are not nil-receiver safe. `IsEnabled` treats a map with only empty values as enabled because it checks length only. `getParam` checks emptiness before trimming, so a whitespace-only value is considered present by the `ok && val != ""` guard but returns empty after trim. Provider names are case-sensitive.

Test signals: `security_test.go` covers agent and Kubernetes auth interactions with token secret presence and auth-method values. Provider, TLS, token, enabled, and trimming behavior are not directly covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security_test.go

Purpose: tests KMS authentication helper predicates for Vault Agent and Kubernetes auth modes.

Important APIs/types/functions: exercises `KeyManagementServiceSpec.IsAgentAuthEnabled` and `KeyManagementServiceSpec.IsK8sAuthEnabled`.

Control flow: each test defines a table of `ConnectionDetails` maps and `TokenSecretName` values. Agent auth cases cover empty config, auth method set to agent with token present, auth method set to token, and auth method set to agent without token. Kubernetes auth cases cover empty config, token-only, Kubernetes auth with token present, unknown auth method, and Kubernetes auth without token.

State and persistence: test-only local KMS specs; no persistence.

Dependencies/integration: uses standard testing only. The tests validate the precedence rule that token secret configuration disables agent/Kubernetes auth helper results.

Risks: tests use literal `"VAULT_AUTH_METHOD"` strings rather than imported constants, so constant drift could break runtime behavior without making the intent obvious. They do not cover provider helpers, TLS helpers, `IsEnabled`, `IsTokenAuthEnabled`, or whitespace trimming.

Test signals: focused coverage for two auth modes and token-secret precedence.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/security_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/spec_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/spec_test.go

Purpose: verifies YAML/JSON unmarshalling compatibility for larger CRD specs: `ClusterSpec` storage/network/mon fields and object-store Swift/Keystone integration fields.

Important APIs/types/functions: tests `ClusterSpec`, `MonSpec`, `NetworkSpec`, `StorageScopeSpec`, `Selection`, `Node`, `ObjectStoreSpec`, `AuthSpec`, `KeystoneSpec`, `ProtocolSpec`, `S3Spec`, and `SwiftSpec`. Local helpers `newTrue`, `newFalse`, `newInt`, and `newString` build pointer values for expected structs.

Control flow: `TestClusterSpecMarshal` converts a YAML cluster spec to JSON, unmarshals into `ClusterSpec`, and compares a fully constructed expected struct containing monitor count, data dir host path, legacy host network, storage selection filters, config map, and a node-specific selection. `TestObjectStoreSpecMarshalSwiftAndKeystone` similarly verifies Keystone auth fields, accepted roles, implicit tenants, token cache/revocation pointer values, service user secret, Swift fields, and S3 Keystone-auth settings. Both tests print raw JSON for debugging.

State and persistence: no persistence. The tests validate serialization shape and pointer field semantics for CRD structs.

Dependencies/integration: depends on Go JSON, Kubernetes YAML conversion, testify, and the local API package. These tests protect backwards-compatible CRD field names and the JSON tags generated/declared on API structs elsewhere.

Risks: `fmt.Printf` produces test output noise. Tests check representative fields but do not validate all cluster or object-store fields. Pointer helper names overlap conceptually with `storage.go`'s unexported `newBool` but are test-local.

Test signals: useful compatibility coverage for cluster storage/network unmarshalling and object-store Swift/Keystone fields, including pointer bool/int/string fields.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/spec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status.go

Purpose: provides shared condition-list helpers for Rook Ceph CRD status fields.

Important APIs/types/functions: `SetStatusCondition(conditions *[]Condition, newCondition Condition)` and `FindStatusCondition(conditions []Condition, conditionType ConditionType) *Condition`.

Control flow: `SetStatusCondition` is nil-pointer safe and returns immediately when the conditions pointer is nil. It captures `now`, finds an existing condition of the same type, and either appends a new condition or updates the existing one. New conditions get `LastTransitionTime` and `LastHeartbeatTime` set to now when the supplied transition time is zero. Existing conditions update status and transition time only when status changes; transition time uses the supplied value if non-zero, otherwise now. Reason and message are always updated. Heartbeat time uses the supplied value if non-zero, otherwise now. `FindStatusCondition` linearly scans and returns a pointer to the matching slice element.

State and persistence: mutates the provided in-memory condition slice. No direct persistence, but callers later persist status through Kubernetes status updates.

Dependencies/integration: depends on `time` and Kubernetes `metav1.Time`. Status accessors in other files return condition pointers intended for this helper.

Risks: returned pointers from `FindStatusCondition` point into the provided slice and can become stale after slice reallocation. `SetStatusCondition` preserves transition time when status is unchanged even if a new transition time is supplied. New-condition logic sets heartbeat only when transition time is zero; if the caller supplies a transition time but no heartbeat, heartbeat remains zero on append.

Test signals: `status_test.go` is based on Kubernetes condition helper tests and covers append, status-change transition update, same-status field update, empty lists, and find present/absent.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status_test.go

Purpose: tests shared condition list update and lookup behavior.

Important APIs/types/functions: exercises `SetStatusCondition` and `FindStatusCondition` with `Condition`, `ConditionType`, Kubernetes condition statuses, and `metav1.Time`.

Control flow: `TestSetStatusCondition` constructs table cases for appending a new condition, updating an existing condition with a status change using supplied transition/heartbeat times, updating reason/message/heartbeat without changing transition time when status is unchanged, and appending to an empty list. It compares whole slices with `reflect.DeepEqual`. `TestFindStatusCondition` checks absent and present condition-type lookup.

State and persistence: test-only local slices; no persistence.

Dependencies/integration: depends on standard `reflect`, `testing`, `time`, and Kubernetes core/metav1 types. The cases are modeled after Kubernetes apimachinery condition behavior.

Risks: tests avoid cases where callers omit timestamps and `SetStatusCondition` uses current time, because those are harder to compare deterministically. Nil `conditions` pointer behavior is not tested. New-condition append with supplied transition but missing heartbeat is not tested.

Test signals: solid deterministic coverage for key condition update semantics and lookup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage.go

Purpose: implements storage-selection helpers for Ceph cluster storage specs, including device-selection inheritance, node lookup, OSD store defaults, and PVC encryption detection.

Important APIs/types/functions: `StoreType`, `StoreTypeBlueStore`, `StoreTypeBlueStoreRDR`, `StorageScopeSpec.AnyUseAllDevices`, `ClearUseAllDevices`, `NodeExists`, `ResolveNode`, `resolveNodeSelection`, `resolveNodeConfig`, `NodeWithNameExists`, `Selection.GetUseAllDevices`, `resolveString`, `newBool`, `NodesByName` (`Len`, `Swap`, `Less`), `StorageScopeSpec.IsOnPVCEncrypted`, `GetOSDStore`, and `GetOSDStoreFlag`.

Control flow: `AnyUseAllDevices` checks cluster-level selection first, then node-level selections. `ClearUseAllDevices` creates one false pointer and assigns it to cluster and all node selections. `ResolveNode` finds a node by name, initializes its config map when nil, then fills missing node selection and config from cluster-level defaults. Selection resolution inherits `UseAllDevices`, device filter, device path filter, devices, and volume claim templates when node-specific values are absent, defaulting use-all-devices to false. Config resolution copies any missing parent config keys without overwriting node-specific keys. Store helpers default to `bluestore` and return either raw type or `--<type>`.

State and persistence: mutates `StorageScopeSpec.Nodes[i]` in place during `ResolveNode`, including inherited pointers/slices/maps. No direct persistence, but resolved specs drive later Ceph OSD reconciliation.

Dependencies/integration: depends on `fmt`. Integrates with cluster CRD storage reconciliation for device discovery, OSD prepare jobs, PVC-backed OSDs, and daemon command-line flags.

Risks: `ResolveNode` returns a pointer into the `Nodes` slice and mutates it; callers must account for side effects. Inherited `UseAllDevices` pointer may alias the cluster-level pointer. `ClearUseAllDevices` assigns the same false pointer to all nodes. `resolveString` cannot distinguish intentionally empty from unset. `NodeExists` and `NodeWithNameExists` duplicate behavior. `GetOSDStoreFlag` uses `fmt.Sprintf` for simple prefixing.

Test signals: `storage_test.go` covers node lookup, missing node resolution, default/inherited/specific selection and config, use-all-devices checks and clearing, device inheritance, node-name existence, and PVC encryption detection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage_test.go

Purpose: unit-tests storage-scope node resolution, use-all-devices behavior, device inheritance, node-name lookup, and PVC encryption detection.

Important APIs/types/functions: exercises `StorageScopeSpec.NodeExists`, `ResolveNode`, `AnyUseAllDevices`, `ClearUseAllDevices`, `NodeWithNameExists`, `IsOnPVCEncrypted`, and indirectly `Selection.GetUseAllDevices`. Fixtures use `Node`, `Selection`, `Device`, and `StorageClassDeviceSet`.

Control flow: tests check node existence with no nodes, one node, and multiple nodes. Resolution tests cover nonexistent node returning nil, default values with no cluster defaults, inheritance of cluster device filters/path filters/devices/config, preservation of node-specific filters/devices/config while inheriting missing config, and cluster-level use-all-devices inheritance. Additional tests verify use-all-devices detection at cluster and node levels, clearing that flag everywhere, cluster device inheritance into nodes without devices, preservation of node devices when set, exact node-name existence, and encrypted PVC-backed device-set detection.

State and persistence: local test structs only. Several tests intentionally rely on `ResolveNode` mutating a node inside the storage spec.

Dependencies/integration: depends on testify. These tests protect OSD selection/defaulting behavior used before device discovery and OSD prepare.

Risks: tests do not cover volume claim template inheritance, `NodesByName` sorting, OSD store default/flag helpers, config-map aliasing, or pointer aliasing after inheritance/clear. There is a spelling mismatch in `TestResolveNodeInherentFromCluster`, but it does not affect behavior.

Test signals: good coverage for main node resolution and use-all-devices branches.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic.go

Purpose: validates Ceph bucket notification topic endpoint specs for HTTP, AMQP, and Kafka.

Important APIs/types/functions: `validateURI`, `ValidateHTTPSpec`, `ValidateAMQPSpec`, `ValidateKafkaSpec`, and `CephBucketTopic.ValidateTopicSpec`.

Control flow: `validateURI` parses a URI with `net/url`, lowercases the parsed scheme, and checks it against an allowed scheme list. HTTP allows `http` and `https`; AMQP allows `amqp` and `amqps`; Kafka allows `kafka`. `ValidateTopicSpec` walks the optional endpoint pointers in order. It validates the present endpoint and enforces exactly one endpoint spec by tracking whether one has already been seen. Multiple endpoints and missing endpoints produce errors.

State and persistence: no persistence or mutation. The function validates in-memory CRD fields before reconciliation.

Dependencies/integration: depends on `net/url`, `strings`, and `github.com/pkg/errors`. Integrates with RGW bucket notification configuration where endpoint type and URI scheme must match.

Risks: `url.Parse` may accept some inputs with empty host or unusual URI shapes; the helper validates only scheme membership. Error text says `"schema"` rather than `"scheme"`. Kafka TLS or SASL options are not validated here beyond URI scheme. Nil endpoint pointer checks happen in `ValidateTopicSpec`, but the individual `Validate*Spec` helpers assume non-nil arguments.

Test signals: `topic_test.go` covers valid and invalid schemes for all endpoint types, one invalid HTTP host case, multiple endpoint rejection, and missing endpoint rejection.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic_test.go -->
# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic_test.go

Purpose: tests bucket topic endpoint validation for HTTP, AMQP, Kafka, multiple endpoints, and missing endpoint specs.

Important APIs/types/functions: exercises `CephBucketTopic.ValidateTopicSpec` and, through it, `ValidateHTTPSpec`, `ValidateAMQPSpec`, `ValidateKafkaSpec`, and `validateURI`. Fixtures use `CephBucketTopic`, `BucketTopicSpec`, `TopicEndpointSpec`, `HTTPEndpointSpec`, `AMQPEndpointSpec`, and `KafkaEndpointSpec`.

Control flow: HTTP tests start with a valid `http://` URI, then mutate to an invalid host with a space, a valid `https://` URI, and an invalid `kaboom://` scheme. AMQP tests cover valid `amqp://`, valid `amqps://`, and invalid `http://`. Kafka tests cover valid `kafka://` and invalid `http://`. The invalid-topic test starts with both Kafka and AMQP endpoints, expects a multiple-endpoint error, removes AMQP and expects success, then removes Kafka and expects a missing-endpoint error.

State and persistence: local topic structs only; no persistence.

Dependencies/integration: depends on testify and Kubernetes `metav1`. These tests protect CRD validation behavior before bucket notification topics are reconciled to RGW.

Risks: tests mutate the same topic object across subtests, making order significant within each parent test. They do not validate empty hosts for otherwise valid schemes, Kafka SSL option consistency, AMQP exchange/ack fields, or exact error messages.

Test signals: focused coverage for endpoint cardinality and URI scheme matching.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/topic_test.go -->
