# subset-b-000443 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemmirror.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemmirror.go

Purpose: generated fake typed client for the namespaced `CephFilesystemMirror` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephFilesystemMirrorInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephFilesystemMirrors` embeds `*gentype.FakeClientWithList[*v1.CephFilesystemMirror, *v1.CephFilesystemMirrorList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephFilesystemMirrors` returns `CephFilesystemMirrorInterface` configured with resource `cephfilesystemmirrors` and kind `CephFilesystemMirror`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephFilesystemMirrors` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephfilesystemmirrors`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemsubvolumegroup.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemsubvolumegroup.go

Purpose: generated fake typed client for the namespaced `CephFilesystemSubVolumeGroup` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephFilesystemSubVolumeGroupInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephFilesystemSubVolumeGroups` embeds `*gentype.FakeClientWithList[*v1.CephFilesystemSubVolumeGroup, *v1.CephFilesystemSubVolumeGroupList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephFilesystemSubVolumeGroups` returns `CephFilesystemSubVolumeGroupInterface` configured with resource `cephfilesystemsubvolumegroups` and kind `CephFilesystemSubVolumeGroup`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephFilesystemSubVolumeGroups` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephfilesystemsubvolumegroups`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephfilesystemsubvolumegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnfs.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnfs.go

Purpose: generated fake typed client for the namespaced `CephNFS` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephNFSInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephNFSes` embeds `*gentype.FakeClientWithList[*v1.CephNFS, *v1.CephNFSList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephNFSes` returns `CephNFSInterface` configured with resource `cephnfses` and kind `CephNFS`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephNFSes` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephnfses`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnvmeofgateway.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnvmeofgateway.go

Purpose: generated fake typed client for the namespaced `CephNVMeOFGateway` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephNVMeOFGatewayInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephNVMeOFGateways` embeds `*gentype.FakeClientWithList[*v1.CephNVMeOFGateway, *v1.CephNVMeOFGatewayList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephNVMeOFGateways` returns `CephNVMeOFGatewayInterface` configured with resource `cephnvmeofgateways` and kind `CephNVMeOFGateway`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephNVMeOFGateways` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephnvmeofgateways`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephnvmeofgateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectrealm.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectrealm.go

Purpose: generated fake typed client for the namespaced `CephObjectRealm` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectRealmInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectRealms` embeds `*gentype.FakeClientWithList[*v1.CephObjectRealm, *v1.CephObjectRealmList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectRealms` returns `CephObjectRealmInterface` configured with resource `cephobjectrealms` and kind `CephObjectRealm`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectRealms` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectrealms`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectrealm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstore.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstore.go

Purpose: generated fake typed client for the namespaced `CephObjectStore` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectStoreInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectStores` embeds `*gentype.FakeClientWithList[*v1.CephObjectStore, *v1.CephObjectStoreList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectStores` returns `CephObjectStoreInterface` configured with resource `cephobjectstores` and kind `CephObjectStore`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectStores` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectstores`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreaccount.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreaccount.go

Purpose: generated fake typed client for the namespaced `CephObjectStoreAccount` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectStoreAccountInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectStoreAccounts` embeds `*gentype.FakeClientWithList[*v1.CephObjectStoreAccount, *v1.CephObjectStoreAccountList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectStoreAccounts` returns `CephObjectStoreAccountInterface` configured with resource `cephobjectstoreaccounts` and kind `CephObjectStoreAccount`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectStoreAccounts` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectstoreaccounts`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreaccount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreuser.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreuser.go

Purpose: generated fake typed client for the namespaced `CephObjectStoreUser` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectStoreUserInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectStoreUsers` embeds `*gentype.FakeClientWithList[*v1.CephObjectStoreUser, *v1.CephObjectStoreUserList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectStoreUsers` returns `CephObjectStoreUserInterface` configured with resource `cephobjectstoreusers` and kind `CephObjectStoreUser`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectStoreUsers` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectstoreusers`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectstoreuser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzone.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzone.go

Purpose: generated fake typed client for the namespaced `CephObjectZone` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectZoneInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectZones` embeds `*gentype.FakeClientWithList[*v1.CephObjectZone, *v1.CephObjectZoneList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectZones` returns `CephObjectZoneInterface` configured with resource `cephobjectzones` and kind `CephObjectZone`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectZones` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectzones`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzonegroup.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzonegroup.go

Purpose: generated fake typed client for the namespaced `CephObjectZoneGroup` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephObjectZoneGroupInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephObjectZoneGroups` embeds `*gentype.FakeClientWithList[*v1.CephObjectZoneGroup, *v1.CephObjectZoneGroupList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephObjectZoneGroups` returns `CephObjectZoneGroupInterface` configured with resource `cephobjectzonegroups` and kind `CephObjectZoneGroup`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephObjectZoneGroups` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephobjectzonegroups`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephobjectzonegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephrbdmirror.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephrbdmirror.go

Purpose: generated fake typed client for the namespaced `CephRBDMirror` custom resource in the Rook Ceph v1 API. It lets unit tests exercise callers of `CephRBDMirrorInterface` without a live Kubernetes API server.

Important APIs/types/functions: `fakeCephRBDMirrors` embeds `*gentype.FakeClientWithList[*v1.CephRBDMirror, *v1.CephRBDMirrorList]` and keeps a `Fake *FakeCephV1` handle. `newFakeCephRBDMirrors` returns `CephRBDMirrorInterface` configured with resource `cephrbdmirrors` and kind `CephRBDMirror`.

Control flow: construction passes the shared fake action recorder, namespace, resource/kind metadata, object and list constructors, list metadata copying, and `gentype.ToPointerSlice`/`FromPointerSlice` adapters into `gentype.NewFakeClientWithList`. All CRUD, watch, patch, delete-collection, and list behavior is inherited from client-go's generic fake client.

State and persistence behavior: state is only the in-memory fake object tracker and action log owned by `FakeCephV1`; no Kubernetes persistence or Ceph state is touched. Namespace scoping is captured at constructor time.

Dependencies and integration points: depends on `github.com/rook/rook/pkg/apis/ceph.rook.io/v1`, the real typed client interface package, and `k8s.io/client-go/gentype`. It is selected by the generated fake CephV1 client when tests call the `CephRBDMirrors` accessor.

Risks: this generated shim can silently diverge if CRD pluralization, kind names, or list item conversion change and client generation is not rerun. Fake behavior does not enforce admission, defaults, status subresources, or API server validation.

Test signals: controller tests should verify expected fake actions for `cephrbdmirrors`, namespace filtering, list metadata propagation, watch/list behavior, and regeneration after API type changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/fake/fake_cephrbdmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/generated_expansion.go -->
# sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/generated_expansion.go

Purpose: generated extension-point file for the Rook Ceph v1 typed clientset. It declares empty expansion interfaces that custom non-generated files can implement to add methods to generated resource interfaces.

Important APIs/types/functions: empty interfaces such as `CephBlockPoolExpansion`, `CephFilesystemExpansion`, `CephNFSExpansion`, `CephObjectStoreExpansion`, `CephNVMeOFGatewayExpansion`, and `CephRBDMirrorExpansion` map one-to-one to generated typed client interfaces.

Control flow: there is no runtime control flow. The Go type system embeds these interfaces into generated client interfaces so future hand-written methods can be added without editing generated files.

State and persistence behavior: no state and no persistence. The file is compile-time API surface only.

Dependencies and integration points: integrated by client-gen output in the same package. It depends on regeneration discipline rather than runtime dependencies.

Risks: removing or renaming an expansion interface breaks generated interface composition and downstream code that relies on custom methods. Since all interfaces are empty today, test failures are mostly compile-time.

Test signals: build coverage is the primary signal; regenerating clients after API additions should preserve an expansion interface for every Rook Ceph v1 resource.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/clientset/versioned/typed/ceph.rook.io/v1/generated_expansion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/interface.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/interface.go

Purpose: generated API-group entry point for external shared informers under `ceph.rook.io`. It exposes versioned informer access while carrying factory, namespace, and list-option filtering state.

Important APIs/types/functions: `Interface` declares `V1() v1.Interface`; `group` stores `internalinterfaces.SharedInformerFactory`, namespace, and `TweakListOptionsFunc`; `New` constructs the group wrapper; `(*group).V1` returns `v1.New(...)`.

Control flow: callers obtain the group from the top-level shared informer factory, call `V1`, and then select concrete resource informers. The namespace and tweak function are threaded into the version implementation unchanged.

State and persistence behavior: no cache state is owned here; it only references the shared factory where informers are cached. No persistent storage is involved.

Dependencies and integration points: bridges `externalversions.SharedInformerFactory.Ceph()` to the generated `ceph.rook.io/v1` informer package. It avoids import cycles by using `internalinterfaces`.

Risks: adding API versions requires regenerating this file so `Interface` exposes them. Incorrect namespace/tweak propagation would make every resource informer in the group watch the wrong scope.

Test signals: compile-time interface checks, factory `Ceph().V1()` access, and filtered/namespaced informer smoke tests cover this layer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpool.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpool.go

Purpose: generated shared informer and lister binding for the `CephBlockPool` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephBlockPoolInformer` exposes `Informer()` and `Lister()`. `NewCephBlockPoolInformer` delegates to `NewFilteredCephBlockPoolInformer`; `NewFilteredCephBlockPoolInformer` builds a `cache.SharedIndexInformer`; `cephBlockPoolInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephBlockPoolLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephBlockPools(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephBlockPool{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephBlockPool`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephBlockPools()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephBlockPools`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpoolradosnamespace.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpoolradosnamespace.go

Purpose: generated shared informer and lister binding for the `CephBlockPoolRadosNamespace` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephBlockPoolRadosNamespaceInformer` exposes `Informer()` and `Lister()`. `NewCephBlockPoolRadosNamespaceInformer` delegates to `NewFilteredCephBlockPoolRadosNamespaceInformer`; `NewFilteredCephBlockPoolRadosNamespaceInformer` builds a `cache.SharedIndexInformer`; `cephBlockPoolRadosNamespaceInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephBlockPoolRadosNamespaceLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephBlockPoolRadosNamespaces(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephBlockPoolRadosNamespace{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephBlockPoolRadosNamespace`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephBlockPoolRadosNamespaces()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephBlockPoolRadosNamespaces`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephblockpoolradosnamespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbucketnotification.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbucketnotification.go

Purpose: generated shared informer and lister binding for the `CephBucketNotification` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephBucketNotificationInformer` exposes `Informer()` and `Lister()`. `NewCephBucketNotificationInformer` delegates to `NewFilteredCephBucketNotificationInformer`; `NewFilteredCephBucketNotificationInformer` builds a `cache.SharedIndexInformer`; `cephBucketNotificationInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephBucketNotificationLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephBucketNotifications(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephBucketNotification{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephBucketNotification`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephBucketNotifications()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephBucketNotifications`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbucketnotification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbuckettopic.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbuckettopic.go

Purpose: generated shared informer and lister binding for the `CephBucketTopic` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephBucketTopicInformer` exposes `Informer()` and `Lister()`. `NewCephBucketTopicInformer` delegates to `NewFilteredCephBucketTopicInformer`; `NewFilteredCephBucketTopicInformer` builds a `cache.SharedIndexInformer`; `cephBucketTopicInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephBucketTopicLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephBucketTopics(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephBucketTopic{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephBucketTopic`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephBucketTopics()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephBucketTopics`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephbuckettopic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephclient.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephclient.go

Purpose: generated shared informer and lister binding for the `CephClient` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephClientInformer` exposes `Informer()` and `Lister()`. `NewCephClientInformer` delegates to `NewFilteredCephClientInformer`; `NewFilteredCephClientInformer` builds a `cache.SharedIndexInformer`; `cephClientInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephClientLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephClients(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephClient{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephClient`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephClients()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephClients`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephclient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcluster.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcluster.go

Purpose: generated shared informer and lister binding for the `CephCluster` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephClusterInformer` exposes `Informer()` and `Lister()`. `NewCephClusterInformer` delegates to `NewFilteredCephClusterInformer`; `NewFilteredCephClusterInformer` builds a `cache.SharedIndexInformer`; `cephClusterInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephClusterLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephClusters(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephCluster{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephCluster`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephClusters()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephClusters`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcosidriver.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcosidriver.go

Purpose: generated shared informer and lister binding for the `CephCOSIDriver` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephCOSIDriverInformer` exposes `Informer()` and `Lister()`. `NewCephCOSIDriverInformer` delegates to `NewFilteredCephCOSIDriverInformer`; `NewFilteredCephCOSIDriverInformer` builds a `cache.SharedIndexInformer`; `cephCOSIDriverInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephCOSIDriverLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephCOSIDrivers(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephCOSIDriver{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephCOSIDriver`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephCOSIDrivers()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephCOSIDrivers`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephcosidriver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go

Purpose: generated shared informer and lister binding for the `CephFilesystem` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephFilesystemInformer` exposes `Informer()` and `Lister()`. `NewCephFilesystemInformer` delegates to `NewFilteredCephFilesystemInformer`; `NewFilteredCephFilesystemInformer` builds a `cache.SharedIndexInformer`; `cephFilesystemInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephFilesystemLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephFilesystems(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephFilesystem{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephFilesystem`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephFilesystems()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephFilesystems`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemmirror.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemmirror.go

Purpose: generated shared informer and lister binding for the `CephFilesystemMirror` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephFilesystemMirrorInformer` exposes `Informer()` and `Lister()`. `NewCephFilesystemMirrorInformer` delegates to `NewFilteredCephFilesystemMirrorInformer`; `NewFilteredCephFilesystemMirrorInformer` builds a `cache.SharedIndexInformer`; `cephFilesystemMirrorInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephFilesystemMirrorLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephFilesystemMirrors(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephFilesystemMirror{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephFilesystemMirror`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephFilesystemMirrors()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephFilesystemMirrors`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go

Purpose: generated shared informer and lister binding for the `CephFilesystemSubVolumeGroup` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephFilesystemSubVolumeGroupInformer` exposes `Informer()` and `Lister()`. `NewCephFilesystemSubVolumeGroupInformer` delegates to `NewFilteredCephFilesystemSubVolumeGroupInformer`; `NewFilteredCephFilesystemSubVolumeGroupInformer` builds a `cache.SharedIndexInformer`; `cephFilesystemSubVolumeGroupInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephFilesystemSubVolumeGroupLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephFilesystemSubVolumeGroups(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephFilesystemSubVolumeGroup{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephFilesystemSubVolumeGroup`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephFilesystemSubVolumeGroups()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephFilesystemSubVolumeGroups`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnfs.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnfs.go

Purpose: generated shared informer and lister binding for the `CephNFS` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephNFSInformer` exposes `Informer()` and `Lister()`. `NewCephNFSInformer` delegates to `NewFilteredCephNFSInformer`; `NewFilteredCephNFSInformer` builds a `cache.SharedIndexInformer`; `cephNFSInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephNFSLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephNFSes(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephNFS{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephNFS`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephNFSes()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephNFSes`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnvmeofgateway.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnvmeofgateway.go

Purpose: generated shared informer and lister binding for the `CephNVMeOFGateway` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephNVMeOFGatewayInformer` exposes `Informer()` and `Lister()`. `NewCephNVMeOFGatewayInformer` delegates to `NewFilteredCephNVMeOFGatewayInformer`; `NewFilteredCephNVMeOFGatewayInformer` builds a `cache.SharedIndexInformer`; `cephNVMeOFGatewayInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephNVMeOFGatewayLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephNVMeOFGateways(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephNVMeOFGateway{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephNVMeOFGateway`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephNVMeOFGateways()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephNVMeOFGateways`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephnvmeofgateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go

Purpose: generated shared informer and lister binding for the `CephObjectRealm` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectRealmInformer` exposes `Informer()` and `Lister()`. `NewCephObjectRealmInformer` delegates to `NewFilteredCephObjectRealmInformer`; `NewFilteredCephObjectRealmInformer` builds a `cache.SharedIndexInformer`; `cephObjectRealmInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectRealmLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectRealms(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectRealm{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectRealm`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectRealms()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectRealms`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectrealm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstore.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstore.go

Purpose: generated shared informer and lister binding for the `CephObjectStore` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectStoreInformer` exposes `Informer()` and `Lister()`. `NewCephObjectStoreInformer` delegates to `NewFilteredCephObjectStoreInformer`; `NewFilteredCephObjectStoreInformer` builds a `cache.SharedIndexInformer`; `cephObjectStoreInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectStoreLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectStores(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectStore{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectStore`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectStores()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectStores`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreaccount.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreaccount.go

Purpose: generated shared informer and lister binding for the `CephObjectStoreAccount` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectStoreAccountInformer` exposes `Informer()` and `Lister()`. `NewCephObjectStoreAccountInformer` delegates to `NewFilteredCephObjectStoreAccountInformer`; `NewFilteredCephObjectStoreAccountInformer` builds a `cache.SharedIndexInformer`; `cephObjectStoreAccountInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectStoreAccountLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectStoreAccounts(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectStoreAccount{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectStoreAccount`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectStoreAccounts()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectStoreAccounts`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreaccount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreuser.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreuser.go

Purpose: generated shared informer and lister binding for the `CephObjectStoreUser` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectStoreUserInformer` exposes `Informer()` and `Lister()`. `NewCephObjectStoreUserInformer` delegates to `NewFilteredCephObjectStoreUserInformer`; `NewFilteredCephObjectStoreUserInformer` builds a `cache.SharedIndexInformer`; `cephObjectStoreUserInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectStoreUserLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectStoreUsers(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectStoreUser{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectStoreUser`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectStoreUsers()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectStoreUsers`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectstoreuser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzone.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzone.go

Purpose: generated shared informer and lister binding for the `CephObjectZone` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectZoneInformer` exposes `Informer()` and `Lister()`. `NewCephObjectZoneInformer` delegates to `NewFilteredCephObjectZoneInformer`; `NewFilteredCephObjectZoneInformer` builds a `cache.SharedIndexInformer`; `cephObjectZoneInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectZoneLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectZones(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectZone{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectZone`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectZones()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectZones`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzonegroup.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzonegroup.go

Purpose: generated shared informer and lister binding for the `CephObjectZoneGroup` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephObjectZoneGroupInformer` exposes `Informer()` and `Lister()`. `NewCephObjectZoneGroupInformer` delegates to `NewFilteredCephObjectZoneGroupInformer`; `NewFilteredCephObjectZoneGroupInformer` builds a `cache.SharedIndexInformer`; `cephObjectZoneGroupInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephObjectZoneGroupLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephObjectZoneGroups(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephObjectZoneGroup{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephObjectZoneGroup`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephObjectZoneGroups()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephObjectZoneGroups`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephobjectzonegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephrbdmirror.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephrbdmirror.go

Purpose: generated shared informer and lister binding for the `CephRBDMirror` Rook Ceph v1 custom resource. It provides cached watch/list access for controllers.

Important APIs/types/functions: `CephRBDMirrorInformer` exposes `Informer()` and `Lister()`. `NewCephRBDMirrorInformer` delegates to `NewFilteredCephRBDMirrorInformer`; `NewFilteredCephRBDMirrorInformer` builds a `cache.SharedIndexInformer`; `cephRBDMirrorInformer` stores factory, namespace, and tweak state; `Lister` returns `cephrookiov1.NewCephRBDMirrorLister`.

Control flow: the `ListWatch` applies `tweakListOptions` when present, then calls `client.CephV1().CephRBDMirrors(namespace).List` or `.Watch`. Both background-context and context-aware list/watch functions are supplied. The factory path calls `InformerFor(&apiscephrookiov1.CephRBDMirror{}, defaultInformer)` so one shared informer instance is reused per type.

State and persistence behavior: object state lives in the client-go cache indexer, keyed by the namespace indexer supplied in `defaultInformer`. The informer reflects Kubernetes API state but does not persist data itself.

Dependencies and integration points: depends on the versioned Rook clientset, `apiscephrookiov1.CephRBDMirror`, generated listers, `cache.ListWatch`, `cache.SharedIndexInformer`, Kubernetes `metav1`, `runtime`, and `watch`. Controllers consume it through `externalversions.Ceph().V1().CephRBDMirrors()`.

Risks: resource accessor, object type, or lister mismatches can compile in some generated paths but deliver the wrong cache to controllers. Tweak functions mutate `ListOptions` for both list and watch, so broken selectors can starve reconciles.

Test signals: informer factory tests should verify list/watch calls to `CephRBDMirrors`, namespace scoping, label/field selector tweak propagation, cache sync, and that `Lister()` reads from the same indexer.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/cephrbdmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go

Purpose: generated version-level informer interface for every `ceph.rook.io/v1` resource. It is the typed menu used by controllers after selecting the Ceph API group and version.

Important APIs/types/functions: `Interface` declares resource methods including `CephBlockPools`, `CephBlockPoolRadosNamespaces`, `CephBucketNotifications`, `CephBucketTopics`, `CephCOSIDrivers`, `CephClients`, `CephClusters`, `CephFilesystems`, `CephFilesystemMirrors`, `CephFilesystemSubVolumeGroups`, `CephNFSes`, `CephNVMeOFGateways`, object-store realm/store/account/user/zone/zonegroup methods, and `CephRBDMirrors`. `version` stores the shared factory, namespace, and tweak function.

Control flow: `New` returns a `version` value. Each method constructs the small per-resource informer wrapper with identical factory/namespace/tweak state; actual informer allocation is deferred until `Informer()` is called on that wrapper.

State and persistence behavior: no local cache or persistence is stored here. The shared factory owns informer caches, started flags, and synchronization state.

Dependencies and integration points: depends on `internalinterfaces.SharedInformerFactory` to avoid cycles and on the sibling generated per-resource informer files. Top-level factories reach this through `Ceph().V1()`.

Risks: omitted methods make resources unavailable to typed controllers; stale method names such as `CephNFSes` or `CephNVMeOFGateways` break generated client compatibility. Because wrappers are cheap, callers must still use the shared factory lifecycle correctly.

Test signals: compile coverage for every generated resource method, generic factory resource lookup, and controller informer construction across all Rook Ceph v1 CRDs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/ceph.rook.io/v1/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/factory.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/factory.go

Purpose: generated top-level shared informer factory for the Rook versioned clientset. It owns informer caching, lifecycle, namespace/filter options, custom resyncs, and transform functions.

Important APIs/types/functions: `SharedInformerOption`, `sharedInformerFactory`, `WithCustomResyncConfig`, `WithTweakListOptions`, `WithNamespace`, `WithTransform`, `NewSharedInformerFactory`, `NewFilteredSharedInformerFactory`, `NewSharedInformerFactoryWithOptions`, `Start`, `Shutdown`, `WaitForCacheSync`, `InformerFor`, the public `SharedInformerFactory` interface, and `Ceph()`.

Control flow: construction initializes maps and applies functional options. `InformerFor` locks, reuses an informer by `reflect.TypeOf(obj)` when present, selects custom or default resync, invokes the resource-specific constructor, applies the optional transform, stores the informer, and returns it. `Start` locks and runs all not-yet-started informers in goroutines. `Shutdown` sets a flag and waits for started goroutines to exit after their stop channel closes. `WaitForCacheSync` snapshots started informers and waits on each cache.

State and persistence behavior: mutable state includes client, namespace, tweak function, default/custom resyncs, transform, informer map, started map, wait group, mutex, and shutdown flag. All state is in-memory process state; persistence is Kubernetes API state watched by informers.

Dependencies and integration points: integrates the generated Rook clientset with client-go `cache.SharedIndexInformer`, `runtime.Object`, `schema.GroupVersionResource`, and the Ceph group informer package. Controllers use this factory to share watches and reduce API server connections.

Risks: informers created after `Start` require another `Start` call; `Start` races with immediate `WaitForCacheSync` if callers do not follow the documented lifecycle. Transform functions affect every informer and can strip fields expected by reconcilers. Wrong custom resync keys silently fall back to the default.

Test signals: lifecycle tests for start idempotency, shutdown blocking/unblocking, informer reuse by type, custom resync application, transform application, namespaced/tweaked factory options, and cache sync reporting.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/generic.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/generic.go

Purpose: generated generic informer lookup for Rook Ceph v1 resources. It lets callers request a `GenericInformer` by `GroupVersionResource` instead of using typed methods.

Important APIs/types/functions: `GenericInformer`, `genericInformer`, `Informer`, `Lister`, and `(*sharedInformerFactory).ForResource`. The switch maps every known Ceph v1 resource plural, including `cephnfses` and `cephnvmeofgateways`, to its typed informer.

Control flow: `ForResource` switches on the requested resource. On a match it constructs `genericInformer{resource: resource.GroupResource(), informer: typed.Informer()}`. `Lister` wraps the shared indexer with `cache.NewGenericLister`. Unknown resources return `fmt.Errorf("no informer found for %v", resource)`.

State and persistence behavior: no state beyond the referenced informer and group resource. The generic lister reads from the same cache owned by the shared factory.

Dependencies and integration points: depends on Rook Ceph v1 scheme group version and client-go cache generic listers. Dynamic controller code and generic utilities use this path when they cannot compile against a typed lister.

Risks: the switch must be regenerated when resources are added or plural names change. Unknown-resource support is explicitly not implemented, so callers need a different dynamic informer for CRDs outside the generated set.

Test signals: table tests for every supported `GroupVersionResource`, error behavior for unknown resources, and confirmation that generic listers share cache state with typed informers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->
# sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go

Purpose: generated small interface package used to connect resource informer packages to the top-level factory without import cycles.

Important APIs/types/functions: `NewInformerFunc`, `SharedInformerFactory`, and `TweakListOptionsFunc`. `NewInformerFunc` receives a versioned Rook client and resync period and returns `cache.SharedIndexInformer`.

Control flow: resource informer wrappers pass their default constructor to `SharedInformerFactory.InformerFor`; tweak functions are invoked by per-resource list/watch closures before API calls.

State and persistence behavior: this file owns no state. It defines contracts implemented by `externalversions.sharedInformerFactory` and consumed by generated resource informers.

Dependencies and integration points: imports the Rook versioned clientset, Kubernetes `metav1.ListOptions`, `runtime.Object`, and client-go cache types. It is a core generated boundary between packages.

Risks: changing these interfaces breaks all generated informer packages. Since the shared interface only exposes `Start` and `InformerFor`, extra top-level factory behavior remains intentionally hidden from resource packages.

Test signals: compile-time conformance of `sharedInformerFactory`, successful resource informer construction, and list-option tweak propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/informers/externalversions/internalinterfaces/factory_interfaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpool.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpool.go

Purpose: generated cache lister for `CephBlockPool` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephBlockPoolLister` supports `List(selector)` and `CephBlockPools(namespace)`. `cephBlockPoolLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephBlockPool]`. `NewCephBlockPoolLister` constructs the indexer with `cephrookiov1.Resource("cephblockpool")`. `CephBlockPoolNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephBlockPool`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpoolradosnamespace.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpoolradosnamespace.go

Purpose: generated cache lister for `CephBlockPoolRadosNamespace` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephBlockPoolRadosNamespaceLister` supports `List(selector)` and `CephBlockPoolRadosNamespaces(namespace)`. `cephBlockPoolRadosNamespaceLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephBlockPoolRadosNamespace]`. `NewCephBlockPoolRadosNamespaceLister` constructs the indexer with `cephrookiov1.Resource("cephblockpoolradosnamespace")`. `CephBlockPoolRadosNamespaceNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephBlockPoolRadosNamespace`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephblockpoolradosnamespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go

Purpose: generated cache lister for `CephBucketNotification` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephBucketNotificationLister` supports `List(selector)` and `CephBucketNotifications(namespace)`. `cephBucketNotificationLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephBucketNotification]`. `NewCephBucketNotificationLister` constructs the indexer with `cephrookiov1.Resource("cephbucketnotification")`. `CephBucketNotificationNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephBucketNotification`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbucketnotification.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbuckettopic.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbuckettopic.go

Purpose: generated cache lister for `CephBucketTopic` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephBucketTopicLister` supports `List(selector)` and `CephBucketTopics(namespace)`. `cephBucketTopicLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephBucketTopic]`. `NewCephBucketTopicLister` constructs the indexer with `cephrookiov1.Resource("cephbuckettopic")`. `CephBucketTopicNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephBucketTopic`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephbuckettopic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephclient.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephclient.go

Purpose: generated cache lister for `CephClient` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephClientLister` supports `List(selector)` and `CephClients(namespace)`. `cephClientLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephClient]`. `NewCephClientLister` constructs the indexer with `cephrookiov1.Resource("cephclient")`. `CephClientNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephClient`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephclient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcluster.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcluster.go

Purpose: generated cache lister for `CephCluster` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephClusterLister` supports `List(selector)` and `CephClusters(namespace)`. `cephClusterLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephCluster]`. `NewCephClusterLister` constructs the indexer with `cephrookiov1.Resource("cephcluster")`. `CephClusterNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephCluster`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcosidriver.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcosidriver.go

Purpose: generated cache lister for `CephCOSIDriver` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephCOSIDriverLister` supports `List(selector)` and `CephCOSIDrivers(namespace)`. `cephCOSIDriverLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephCOSIDriver]`. `NewCephCOSIDriverLister` constructs the indexer with `cephrookiov1.Resource("cephcosidriver")`. `CephCOSIDriverNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephCOSIDriver`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephcosidriver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystem.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystem.go

Purpose: generated cache lister for `CephFilesystem` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephFilesystemLister` supports `List(selector)` and `CephFilesystems(namespace)`. `cephFilesystemLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephFilesystem]`. `NewCephFilesystemLister` constructs the indexer with `cephrookiov1.Resource("cephfilesystem")`. `CephFilesystemNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephFilesystem`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemmirror.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemmirror.go

Purpose: generated cache lister for `CephFilesystemMirror` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephFilesystemMirrorLister` supports `List(selector)` and `CephFilesystemMirrors(namespace)`. `cephFilesystemMirrorLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephFilesystemMirror]`. `NewCephFilesystemMirrorLister` constructs the indexer with `cephrookiov1.Resource("cephfilesystemmirror")`. `CephFilesystemMirrorNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephFilesystemMirror`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go

Purpose: generated cache lister for `CephFilesystemSubVolumeGroup` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephFilesystemSubVolumeGroupLister` supports `List(selector)` and `CephFilesystemSubVolumeGroups(namespace)`. `cephFilesystemSubVolumeGroupLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephFilesystemSubVolumeGroup]`. `NewCephFilesystemSubVolumeGroupLister` constructs the indexer with `cephrookiov1.Resource("cephfilesystemsubvolumegroup")`. `CephFilesystemSubVolumeGroupNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephFilesystemSubVolumeGroup`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephfilesystemsubvolumegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnfs.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnfs.go

Purpose: generated cache lister for `CephNFS` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephNFSLister` supports `List(selector)` and `CephNFSes(namespace)`. `cephNFSLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephNFS]`. `NewCephNFSLister` constructs the indexer with `cephrookiov1.Resource("cephnfs")`. `CephNFSNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephNFS`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnvmeofgateway.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnvmeofgateway.go

Purpose: generated cache lister for `CephNVMeOFGateway` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephNVMeOFGatewayLister` supports `List(selector)` and `CephNVMeOFGateways(namespace)`. `cephNVMeOFGatewayLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephNVMeOFGateway]`. `NewCephNVMeOFGatewayLister` constructs the indexer with `cephrookiov1.Resource("cephnvmeofgateway")`. `CephNVMeOFGatewayNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephNVMeOFGateway`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephnvmeofgateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectrealm.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectrealm.go

Purpose: generated cache lister for `CephObjectRealm` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectRealmLister` supports `List(selector)` and `CephObjectRealms(namespace)`. `cephObjectRealmLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectRealm]`. `NewCephObjectRealmLister` constructs the indexer with `cephrookiov1.Resource("cephobjectrealm")`. `CephObjectRealmNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectRealm`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectrealm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstore.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstore.go

Purpose: generated cache lister for `CephObjectStore` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectStoreLister` supports `List(selector)` and `CephObjectStores(namespace)`. `cephObjectStoreLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectStore]`. `NewCephObjectStoreLister` constructs the indexer with `cephrookiov1.Resource("cephobjectstore")`. `CephObjectStoreNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectStore`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreaccount.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreaccount.go

Purpose: generated cache lister for `CephObjectStoreAccount` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectStoreAccountLister` supports `List(selector)` and `CephObjectStoreAccounts(namespace)`. `cephObjectStoreAccountLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectStoreAccount]`. `NewCephObjectStoreAccountLister` constructs the indexer with `cephrookiov1.Resource("cephobjectstoreaccount")`. `CephObjectStoreAccountNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectStoreAccount`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreaccount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreuser.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreuser.go

Purpose: generated cache lister for `CephObjectStoreUser` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectStoreUserLister` supports `List(selector)` and `CephObjectStoreUsers(namespace)`. `cephObjectStoreUserLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectStoreUser]`. `NewCephObjectStoreUserLister` constructs the indexer with `cephrookiov1.Resource("cephobjectstoreuser")`. `CephObjectStoreUserNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectStoreUser`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectstoreuser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzone.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzone.go

Purpose: generated cache lister for `CephObjectZone` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectZoneLister` supports `List(selector)` and `CephObjectZones(namespace)`. `cephObjectZoneLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectZone]`. `NewCephObjectZoneLister` constructs the indexer with `cephrookiov1.Resource("cephobjectzone")`. `CephObjectZoneNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectZone`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzonegroup.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzonegroup.go

Purpose: generated cache lister for `CephObjectZoneGroup` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephObjectZoneGroupLister` supports `List(selector)` and `CephObjectZoneGroups(namespace)`. `cephObjectZoneGroupLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephObjectZoneGroup]`. `NewCephObjectZoneGroupLister` constructs the indexer with `cephrookiov1.Resource("cephobjectzonegroup")`. `CephObjectZoneGroupNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephObjectZoneGroup`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephobjectzonegroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephrbdmirror.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephrbdmirror.go

Purpose: generated cache lister for `CephRBDMirror` objects. It gives controllers read-only typed access to objects already stored in a shared informer indexer.

Important APIs/types/functions: `CephRBDMirrorLister` supports `List(selector)` and `CephRBDMirrors(namespace)`. `cephRBDMirrorLister` embeds `listers.ResourceIndexer[*cephrookiov1.CephRBDMirror]`. `NewCephRBDMirrorLister` constructs the indexer with `cephrookiov1.Resource("cephrbdmirror")`. `CephRBDMirrorNamespaceLister` supports namespace-scoped `List` and `Get`.

Control flow: callers receive the lister from the matching informer, then list across the cache or request a namespace lister. Namespace listers are created with `listers.NewNamespaced` and delegate label filtering and name lookup to client-go's generic indexer implementation.

State and persistence behavior: the lister has no storage of its own; it wraps a `cache.Indexer` populated by the informer. Returned objects are documented as read-only because mutating cached pointers can corrupt controller behavior.

Dependencies and integration points: depends on the Rook Ceph v1 API type, `labels.Selector`, client-go generic listers, and the informer indexer. Reconcilers use this file through generated informer `Lister()` methods.

Risks: wrong resource strings degrade error messages and generic behavior; namespace-index assumptions require informers to use the namespace indexer. Callers must deep-copy before mutation.

Test signals: list/get behavior for `CephRBDMirror`, namespace filtering, not-found errors, label selector behavior, and read-only usage patterns in reconcilers.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/cephrbdmirror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/expansion_generated.go -->
# sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/expansion_generated.go

Purpose: generated extension-point file for Rook Ceph v1 listers. It declares empty lister and namespace-lister expansion interfaces for every generated resource.

Important APIs/types/functions: pairs such as `CephBlockPoolListerExpansion` and `CephBlockPoolNamespaceListerExpansion`, plus equivalent pairs for Rados namespaces, bucket notification/topic, COSI driver, client, cluster, filesystem, NFS, NVMe-oF gateway, object-store resources, and RBD mirror.

Control flow: no runtime control flow exists. Generated lister interfaces embed these empty interfaces so custom methods can be added from non-generated files without modifying generated output.

State and persistence behavior: no state or persistence. This is compile-time interface shape only.

Dependencies and integration points: consumed by generated lister interfaces in the same package and by any hand-written lister extensions.

Risks: stale or missing expansion interfaces break regeneration symmetry or downstream custom extensions. Empty interfaces mean build coverage is the main protection.

Test signals: successful package builds and regenerated lister output after API-resource changes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/client/listers/ceph.rook.io/v1/expansion_generated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/context.go -->
# sources/control-plane/rook/pkg/clusterd/context.go

Purpose: defines `clusterd.Context`, the shared dependency container used by Rook cluster orchestration and daemons when applying Kubernetes and Ceph configuration.

Important APIs/types/functions: the `Context` struct carries `KubeConfig`, core `Clientset`, controller-runtime `Client`, Rook typed clientset, API extensions client, local and remote command executors, config paths, CNI network client, and discovered `Devices`.

Control flow: this file has no functions; callers construct and pass `Context` through operator and daemon code so lower layers can access Kubernetes, execution, configuration, networking, and device inventory dependencies consistently.

State and persistence behavior: the struct is process-local state. Its clients talk to Kubernetes persistence, executors run host or pod commands, and `Devices` snapshots local disk discovery results.

Dependencies and integration points: integrates Kubernetes client-go, controller-runtime, Rook generated clients, CNI network attachment clients, Rook exec abstractions, and `sys.LocalDisk` inventory. Cleanup and discovery code in this subset consumes it directly.

Risks: because the struct is broad and mutable, nil fields can panic in consumers that assume a fully initialized context. Tests often populate only the executor, so new consumers should keep dependency requirements explicit.

Test signals: construction paths for operator contexts, unit tests with partial contexts, and integration tests that exercise Kubernetes clients, remote execution, and device inventory together.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk.go -->
# sources/control-plane/rook/pkg/clusterd/disk.go

Purpose: discovers and filters local block devices for Rook cluster/device orchestration, including lsblk and udev metadata population and policy for supported device types.

Important APIs/types/functions: `supportedDeviceType`, `GetDeviceEmpty`, `ignoreDevice`, `DiscoverDevicesWithFilter`, `deviceMatchWithFilter`, `DiscoverDevices`, `PopulateDeviceInfo`, `PopulateDeviceUdevInfo`, and `getAllowLoopDevices`. Package variables include `isRBD`, `listAllDevices`, and the `dm-` allow pattern.

Control flow: `DiscoverDevicesWithFilter` lists device names, skips RBD devices, applies regex/meta-device filters, populates lsblk properties, best-effort augments udev info, skips parent disks with child partitions, and returns the remaining `LocalDisk` list. `PopulateDeviceInfo` validates type, optionally reads disk UUID, parses size/rotational/read-only fields, and copies path/filesystem/mount metadata. `PopulateDeviceUdevInfo` overlays DEVLINKS, filesystem, serial, vendor, model, and WWN fields.

State and persistence behavior: no persistent writes. It reads host block-device state through the injected executor and environment variable `CEPH_VOLUME_ALLOW_LOOP_DEVICES` to decide loop-device support.

Dependencies and integration points: depends on Rook `exec.Executor`, `sys` lsblk/udev helpers, capnslog, regexp, and OS environment. The resulting `LocalDisk` values feed OSD discovery and cluster context device lists.

Risks: invalid regex filters silently reject devices; `dm-` devices are always allowed for metadata devices; udev failures are logged but not fatal, which can leave filesystem detection less accurate. Parent/child detection assumes lsblk child output length semantics.

Test signals: filter matching, RBD ignore regex, supported type matrix, loop-device env behavior, lsblk parsing, udev overlay precedence, child-device skipping, and error/log behavior for command failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk_test.go -->
# sources/control-plane/rook/pkg/clusterd/disk_test.go

Purpose: unit tests for local disk discovery helpers in `clusterd/disk.go`.

Important APIs/types/functions: `TestDiscoverDevices`, `TestDeviceMatchWithFilter`, and `TestIgnoreDevice` use `exectest.MockExecutor` and testify assertions.

Control flow: `TestDiscoverDevices` verifies an empty mock command output yields no devices and no error. `TestDeviceMatchWithFilter` covers negative regex matches, positive NVMe regex matches, `all`, explicit meta-device allowance, and `dm-` allowance. `TestIgnoreDevice` table-tests acceptable and unacceptable RBD-like names.

State and persistence behavior: tests are in-memory and do not touch host disks; the mock executor isolates command execution.

Dependencies and integration points: depends on the production discovery functions, Rook exec test helpers, and `stretchr/testify/assert`.

Risks: current tests do not cover lsblk property parsing, udev fallback, unsupported device types, child-device skipping, invalid regex behavior, or loop-device environment handling.

Test signals: these tests protect the highest-risk filter and RBD ignore policies while leaving deeper device population behavior to other tests or integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go

Purpose: implements OSD disk sanitization for cleanup jobs, covering LVM OSD zapping, raw device shredding/zapping, encrypted device handling, and metadata/WAL device cleanup.

Important APIs/types/functions: `DiskSanitizer`, `ShredCommand`, `NewDiskSanitizer`, `StartSanitizeDisks`, `SanitizeRawDisk`, `SanitizeLVMDisk`, `wipeLVM`, `returnPVDevice`, `buildDataSource`, `buildShredArgs`, `buildQuickShredCommands`, `buildShredCommands`, and `executeSanitizeCommand`.

Control flow: `StartSanitizeDisks` lists LVM OSDs then raw OSDs through ceph-volume helpers and sanitizes each set. Raw sanitization launches one goroutine per OSD. LVM sanitization records each LV's PV, runs `ceph-volume lvm zap --osd-id --destroy` concurrently, waits, then sanitizes PV devices. `executeSanitizeCommand` resolves encrypted backing devices, removes dm mappings, then runs quick zap or full `shred` commands for block, metadata, and WAL paths.

State and persistence behavior: no internal persistent state, but commands destructively modify disks and LVM metadata. The sanitizer depends on `SanitizeDisksSpec` method, data source, and iteration count; logs record command output.

Dependencies and integration points: integrates `clusterd.Context` executor, Ceph cluster info, CephVolume OSD discovery, operator OSD info structs, encryption helpers, and Ceph CRD sanitize policy.

Risks: destructive operations run concurrently and errors are logged but often not returned to a caller. `returnPVDevice(...)[0]` assumes the LVS command produced at least one colon-delimited value. Full shred command construction around zero/random data source must match user expectations.

Test signals: command construction for quick/complete zero/random modes, encrypted path substitution, LVM PV parsing failures, concurrent error handling, metadata/WAL coverage, and real cleanup job integration on test devices.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go

Purpose: unit tests for disk sanitizer command construction.

Important APIs/types/functions: `TestBuildDataSource` verifies `/dev/zero`; `TestBuildShredCommands` table-tests quick and complete sanitize methods using `DiskSanitizer.buildShredCommands`.

Control flow: tests build a mock `clusterd.Context`, create sanitize specs, and compare resulting `ShredCommand` slices with expected `ceph-volume lvm zap` or `shred` arguments.

State and persistence behavior: no disks are modified. Mock executor stubs unrelated lsblk/sgdisk calls but the tested functions mostly avoid command execution.

Dependencies and integration points: depends on cleanup command builders, Ceph API sanitize enum values, Rook exec test helpers, and testify/assert.

Risks: tests do not cover actual `StartSanitizeDisks`, goroutine behavior, encrypted devices, LVM PV parsing, or command-execution error paths.

Test signals: protects user-visible sanitize method/data-source translation, especially `--random-source=/dev/zero`, `--zero`, iteration count, and quick-mode zap behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/disk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go

Purpose: cleans host-path data left by a Rook Ceph cluster, including namespace data directories, monitor directories whose key matches the current mon secret, exporter data, and CSI driver directories.

Important APIs/types/functions: `StartHostPathCleanup`, `cleanCSIDirs`, `cleanExporterDir`, `cleanMonDirs`, and `secretKeyMatch`.

Control flow: `StartHostPathCleanup` removes `dataDirHostPath/namespaceDir`, then calls monitor, exporter, and CSI cleanup helpers. `cleanMonDirs` glob-matches `mon-*`, checks each keyring with `secretKeyMatch`, and deletes only matching monitor directories. `cleanCSIDirs` removes directories whose names end in `.csi.ceph.com`; `cleanExporterDir` removes `exporter` if present.

State and persistence behavior: this file performs filesystem deletion via `os.RemoveAll`. Secret matching reads `monDir/data/keyring` and compares the extracted key to the supplied mon secret to avoid deleting unrelated monitor data.

Dependencies and integration points: depends on `os`, `filepath`, `path`, Rook operator key extraction, and cleanup logging. It is invoked by cleanup jobs for host-mounted Rook data directories.

Risks: `filepath.Join(monDir, "/data/keyring")` uses an absolute second path component, so path-cleaning behavior deserves attention. Recursive deletes are broad and depend on correct inputs. CSI cleanup deletes all matching suffix directories under the data root.

Test signals: monitor secret match/mismatch, missing keyring behavior, exporter deletion, CSI suffix deletion, namespace data deletion, invalid glob/read-dir paths, and path traversal/absolute-path safeguards.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go

Purpose: unit tests for host-path cleanup helpers.

Important APIs/types/functions: `Test_cleanCSIDirs`, `Test_cleanExporterDir`, `Test_monDir`, and `Test_secretKeyMatch` use temporary directories and real filesystem operations.

Control flow: tests create CSI, exporter, and monitor/keyring directories under `t.TempDir`, invoke cleanup helpers, and assert expected deletion or retention. `Test_secretKeyMatch` checks both matching and mismatching extracted keys.

State and persistence behavior: all state is temporary filesystem state owned by the test process. No Kubernetes or Ceph cluster is contacted.

Dependencies and integration points: tests production cleanup helpers, Go `os`/`filepath`, and testify assertions.

Risks: `Test_cleanCSIDirs` appears to assert the RBD path twice and does not independently assert the CephFS CSI path after cleanup. Broader `StartHostPathCleanup` and error branches are not covered.

Test signals: protects key deletion safety for monitor directories and basic recursive deletion of exporter/CSI paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/hostpath_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go

Purpose: removes RBD images, snapshots, trash entries, and active clients for either a `CephBlockPoolRadosNamespace` or an entire `CephBlockPool`.

Important APIs/types/functions: `RadosNamespaceCleanup`, `cleanupImages`, `BlockPoolCleanup`, `blocklistClients`, `getClients`, and constant `ClientBlocklistDuration` set to `1200` seconds.

Control flow: cleanup lists images in the pool/namespace, blocklists all watchers found from image status, then for each image lists and deletes snapshots, moves the image to trash, and schedules trash deletion by image ID. Errors per image/snapshot are logged and accumulated in `retErr`, while blocklist/list failures abort earlier.

State and persistence behavior: no local state persists, but Ceph cluster state is changed through RBD snapshot deletion, image trash operations, trash-removal tasks, and blocklist entries. The client set is a Kubernetes `sets.Set[string]` used for deduplication.

Dependencies and integration points: depends on `clusterd.Context`, Ceph client helpers for RBD/rados namespace operations, and Rook cleanup logging. It is likely called during CR deletion finalization for block pools and Rados namespaces.

Risks: blocklisting every watcher can disrupt active clients; only the last per-image error is returned; trash move/delete ordering assumes image ID remains valid. Empty namespace and pool cleanup share the same path, so namespace argument formatting must stay correct.

Test signals: no-image cleanup, snapshot deletion, namespace vs pool command paths, watcher deduplication and blocklist failures, partial failure accumulation, and trash task command construction.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go

Purpose: unit tests for RBD cleanup in block pools and Rados namespaces.

Important APIs/types/functions: `TestRadosNamespace`, `TestBlockPoolCleanup`, and `TestGetClientIPs` use mock executor command argument assertions with fixture JSON for images, snapshots, and watcher status.

Control flow: tests cover empty image lists, images with snapshots, snapshot removal, trash move, trash deletion task formatting with and without namespace, and watcher-client deduplication across images.

State and persistence behavior: all Ceph operations are mocked through `MockExecuteCommandWithOutput`; no real cluster is mutated.

Dependencies and integration points: depends on cleanup functions, Ceph client command wrappers, `clusterd.Context`, exec test mocks, and testify assertions.

Risks: tests emphasize success paths and command shape, but do not cover blocklist command failure, snapshot/list failure accumulation, trash failures, or malformed JSON from Ceph commands.

Test signals: strong signal for command argument compatibility between cleanup code and Ceph client helpers for namespace-aware and pool-wide RBD deletion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/radosnamespace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go

Purpose: cleans CephFS subvolumes inside a subvolume group before `CephFilesystemSubVolumeGroup` deletion, including CSI OMAP entries, pending clone cancellation, snapshot deletion, and subvolume removal.

Important APIs/types/functions: `SubVolumeGroupCleanup`, `CancelPendingClones`, `DeleteSubVolumeSnapshots`, `CleanUpOMAPDetails`, and `getOMAPValue`.

Control flow: `SubVolumeGroupCleanup` lists subvolumes for the filesystem/group. For each subvolume it derives and deletes CSI OMAP state, lists snapshots, cancels pending clones for those snapshots, deletes snapshots, and finally deletes the subvolume. It logs each failure and returns a wrapped aggregate last error if cleanup did not fully succeed.

State and persistence behavior: local state is only temporary lists and `retErr`; persistent effects occur in CephFS and RADOS OMAP objects through Ceph client commands. `getOMAPValue` derives `csi.volume.<uuid>` from CSI-style subvolume names.

Dependencies and integration points: depends on `clusterd.Context`, Ceph client helpers for CephFS subvolume/snapshot/clone commands and OMAP operations, CSI naming conventions, and cleanup logging.

Risks: non-CSI subvolume names fail OMAP derivation and mark cleanup failed. Returning only the latest error can hide earlier failures. Pending clone cancellation aborts on the first clone error for a snapshot set. OMAP deletion before snapshot/subvolume removal may leave inconsistent CSI metadata on later failures.

Test signals: empty group, CSI-named subvolume cleanup, OMAP value/key deletion, pending clone cancellation, snapshot deletion, subvolume deletion, invalid subvolume names, and partial error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go -->
# sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go

Purpose: unit tests for CephFS subvolume group cleanup and OMAP-name derivation.

Important APIs/types/functions: `TestSubVolumeGroupCleanup` and `TestGetOmapValue` use mocked command execution with timeout and fixture JSON for subvolumes, snapshots, and pending clones.

Control flow: tests cover an empty subvolume group and a group with one CSI-named subvolume, OMAP lookup/deletion, snapshot listing, pending clone cancellation, snapshot deletion, and forced subvolume removal. `TestGetOmapValue` verifies valid CSI name parsing and invalid-name rejection.

State and persistence behavior: all Ceph commands are mocked; no CephFS or RADOS state is changed.

Dependencies and integration points: depends on Ceph client wrappers invoked by cleanup code, `clusterd.Context`, exec test mocks, and testify assertions.

Risks: error paths, multiple subvolumes/snapshots, malformed command output, and partial cleanup rollback are not covered. The test fixtures pin the expected CSI naming convention.

Test signals: good coverage of expected command ordering and argument shape for the successful cleanup path.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/cleanup/subvolumegroups_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/auth.go -->
# sources/control-plane/rook/pkg/daemon/ceph/client/auth.go

Purpose: wraps Ceph CLI auth operations for cephx users: get/create keys, update/read caps, rotate keys, delete users, and list auth entities.

Important APIs/types/functions: `AuthListOutput`, `AuthListEntry`, `AuthGetKey`, `AuthGetOrCreateKey`, `AuthUpdateCaps`, `AuthGetCaps`, `AuthRotate`, `AuthDelete`, `parseAuthKey`, and `AuthList`.

Control flow: each public function builds Ceph command args and executes `NewCephCommand(context, clusterInfo, args).Run()`. Key-get/create parse JSON `key`. `AuthGetCaps` unmarshals `auth get` output as a slice and extracts `mon`, `mds`, `mgr`, and `osd` caps when present. `AuthRotate` handles `EINVAL` specially for Ceph versions that lack `auth rotate`, unmarshals result arrays, warns on multiple results, and returns the first key. `AuthList` unmarshals `auth_dump` entries.

State and persistence behavior: no local persistence; functions mutate or read Ceph monitor auth state. Returned keys are sensitive secrets and logs avoid dumping successful key material, though debug traces can show failed raw auth-list responses.

Dependencies and integration points: depends on `clusterd.Context`, `ClusterInfo`, `NewCephCommand`, JSON decoding, Rook exec exit-status helpers, and syscall errno. Operator code uses these helpers to manage daemon/client credentials.

Risks: several JSON paths use unchecked type assertions and can panic on unexpected Ceph output. `parseAuthKey` assumes a top-level `key` string. Rotate compatibility depends on exit status mapping. Caps extraction ignores cap names outside the four known daemon classes.

Test signals: key parsing, malformed JSON, missing key/caps fields, rotate unsupported EINVAL, multiple/no rotate results, command argument construction, delete/list failures, and sensitive logging behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/daemon/ceph/client/auth.go -->
