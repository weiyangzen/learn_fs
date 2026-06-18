# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/spec_test.go

Purpose: verifies YAML/JSON unmarshalling compatibility for larger CRD specs: `ClusterSpec` storage/network/mon fields and object-store Swift/Keystone integration fields.

Important APIs/types/functions: tests `ClusterSpec`, `MonSpec`, `NetworkSpec`, `StorageScopeSpec`, `Selection`, `Node`, `ObjectStoreSpec`, `AuthSpec`, `KeystoneSpec`, `ProtocolSpec`, `S3Spec`, and `SwiftSpec`. Local helpers `newTrue`, `newFalse`, `newInt`, and `newString` build pointer values for expected structs.

Control flow: `TestClusterSpecMarshal` converts a YAML cluster spec to JSON, unmarshals into `ClusterSpec`, and compares a fully constructed expected struct containing monitor count, data dir host path, legacy host network, storage selection filters, config map, and a node-specific selection. `TestObjectStoreSpecMarshalSwiftAndKeystone` similarly verifies Keystone auth fields, accepted roles, implicit tenants, token cache/revocation pointer values, service user secret, Swift fields, and S3 Keystone-auth settings. Both tests print raw JSON for debugging.

State and persistence: no persistence. The tests validate serialization shape and pointer field semantics for CRD structs.

Dependencies/integration: depends on Go JSON, Kubernetes YAML conversion, testify, and the local API package. These tests protect backwards-compatible CRD field names and the JSON tags generated/declared on API structs elsewhere.

Risks: `fmt.Printf` produces test output noise. Tests check representative fields but do not validate all cluster or object-store fields. Pointer helper names overlap conceptually with `storage.go`'s unexported `newBool` but are test-local.

Test signals: useful compatibility coverage for cluster storage/network unmarshalling and object-store Swift/Keystone fields, including pointer bool/int/string fields.
