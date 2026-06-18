# sources/control-plane/rook/pkg/operator/ceph/object/status_test.go

Purpose: this file tests `buildStatusInfo` for `CephObjectStore` endpoint reporting. It verifies how the status `Info` map chooses HTTP, HTTPS, dual-port, and explicitly advertised endpoints.

Important APIs and test cases: `TestBuildStatusInfo` builds a base `CephObjectStore` and mutates gateway ports and hosting advertise endpoint settings. It checks `endpoint` and `secureEndpoint` keys for regular service DNS output and for advertiseEndpoint override behavior.

Control flow and state behavior: each scenario deep-copies a base CR, sets `Spec.Gateway.Port`, `Spec.Gateway.SecurePort`, `SSLCertificateRef`, or `Spec.Hosting.AdvertiseEndpoint`, then calls `buildStatusInfo` and asserts exact URLs. There are no Kubernetes clients, no persisted status updates, and no reconcile loop.

Dependencies and integration points: the test uses `cephv1.CephObjectStore`, `cephv1.ObjectStoreHostingSpec`, `cephv1.ObjectEndpointSpec`, Kubernetes metadata, and `testify/assert`. Expected URLs encode the stable service DNS naming convention `rook-ceph-rgw-<store>.<namespace>.svc`.

Risks and gaps: this test does not cover `updateStatus`, not-found behavior, retry conflicts, delete-phase behavior, selector generation, endpoint slice arrays, replica counts, or CephX daemon status. It specifically guards the legacy info-map URL behavior, including the rule that an explicit advertise endpoint suppresses `secureEndpoint` even when both gateway ports are enabled.

Test signals: the file provides focused, stable regression signals for user-visible endpoint fields. Failures usually indicate a change in service DNS naming, advertiseEndpoint precedence, or HTTPS preference rules.
