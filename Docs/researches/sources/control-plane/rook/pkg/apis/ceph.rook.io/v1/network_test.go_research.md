# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/network_test.go

Purpose: unit-tests the Ceph `NetworkSpec` compatibility, validation, host-network interpretation, address-range validation, and Multus network-selection serialization behavior. It is a test-only file for API helper behavior defined in the same `v1` package.

Important APIs/types/functions: tests cover `NetworkSpec`, `NetworkProviderDefault`, `NetworkProviderHost`, `NetworkProviderMultus`, `ValidateNetworkSpec`, `NetworkSpec.IsHost`, `SetEnforceHostNetwork`, `AddressRangesSpec.IsEmpty`, `AddressRangesSpec.Validate`, `NetworkSpec.GetNetworkSelection`, and `NetworkSelectionsToAnnotationValue`. It also exercises `CIDR`, `CephNetworkPublic`, `CephNetworkCluster`, and the network-attachment-definition client `NetworkSelectionElement`.

Control flow: YAML snippets are converted to JSON and unmarshaled into API structs to verify CRD wire compatibility. Validation tests build small `NetworkSpec` instances and assert which provider/host-network combinations are rejected. Host-network tests toggle the package-global enforce flag and combine provider values with legacy `HostNetwork`. The address range table validates IPv4, IPv6, IPv4-embedded IPv6, and malformed CIDR inputs. The Multus table calls `GetNetworkSelection` for requested Ceph network types, collects selection objects and errors, and then serializes all selections through `NetworkSelectionsToAnnotationValue`.

State and persistence: the file has no persistence. It mutates only local test objects plus the global host-network enforcement setting via `SetEnforceHostNetwork`, resetting it between scenarios to avoid cross-test leakage.

Dependencies/integration: depends on Go JSON unmarshalling, Kubernetes YAML conversion, testify assertions, and `k8snetworkplumbingwg/network-attachment-definition-client` types. These tests protect the API contract used by operators that translate `NetworkSpec` to pod host networking or Multus annotations.

Risks: tests touch a package-level enforcement flag, so parallelization would need care. The annotation tests compare exact compact JSON strings, making output ordering part of the contract. The suite intentionally tests only a subset of CIDR possibilities because validation is expected to delegate to Go stdlib parsing.

Test signals: strong coverage for legacy `hostNetwork`, provider conflict validation, enforced host-network override, invalid provider fallback, empty/non-empty address ranges, aggregated invalid CIDR counts, JSON and non-JSON Multus inputs, mixed selector forms, unknown selector keys, legacy single-object JSON, and invalid selector parsing.
