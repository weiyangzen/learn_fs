# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/object_test.go

Purpose: validates Ceph object-store API helper behavior, especially object-store validation, TLS enablement, security cipher constraints, and advertised endpoint URL selection.

Important APIs/types/functions: tests `ValidateObjectSpec`, `validateObjectStoreSecurity`, `ObjectStoreSpec.IsTLSEnabled`, and `CephObjectStore.GetAdvertiseEndpointUrl`. Fixtures use `CephObjectStore`, `ObjectStoreSpec`, `GatewaySpec`, `ObjectStoreHostingSpec`, `ObjectEndpointSpec`, `ObjectStoreSecuritySpec`, `SslOptionsSpec`, `EndpointAddress`, `RGWServiceSpec`, `Annotations`, and `ServiceServingCertKey`.

Control flow: the validation test starts from a minimal valid store, mutates gateway ports and object metadata to trigger errors, then runs hosting subtests for invalid wildcard/empty advertise DNS, port 0, port 65536, and invalid hosting DNS names with assertions that valid names are not incorrectly reported. Security subtests verify TLS 1.3 cipher suites are allowed, legacy ciphers fail when all TLS 1.2-or-below options are disabled, then pass when TLS 1.2 is enabled, and that ciphers and cipher suites can coexist. TLS enablement subtests combine secure ports, certificate refs, and OpenShift service-serving cert annotations. The advertise URL table builds internal stores, external IPv4/IPv6/hostname stores, nil hosting, nil advertise endpoint, HTTP override, HTTPS override, cert removal, and missing port cases.

State and persistence: test-only local state. The advertise URL table mutates copied CRD structs via helper closures; no Kubernetes API or persistent state is touched.

Dependencies/integration: uses testify and Kubernetes `metav1`. The tests freeze stable behavior for service-domain naming, external endpoint precedence, IPv6 URL formatting, and OpenShift certificate-driven TLS.

Risks: several helper closures mutate the object they receive; table entries are built eagerly, so reuse must be understood before extending tests. `GetAdvertiseEndpointUrl` tests assume only the first external endpoint is used. Error checks usually look for substrings, not full error values.

Test signals: broad branch coverage for object-store validation and URL behavior. It does not directly test `IsMultisite`, `IsRGWDashboardEnabled`, `IsHostNetwork`, `ObjectRealmSpec.IsPullRealm`, status-condition accessors, or `EndpointAddress.String` outside its use in advertise endpoint selection.
