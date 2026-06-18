# sources/control-plane/rook/pkg/operator/ceph/object/config_test.go

## Purpose
`config_test.go` verifies the low-level RGW configuration builders used by object-store reconciliation, especially frontend formatting and monitor config generation.

## Important APIs, Types, and Functions
`newConfig()` creates a minimal `clusterConfig` with Squid version, non-host networking, and a fake Kubernetes client. `TestPortString`, `TestRgwFrontendStr`, and `TestBuildSslOptions` exercise gateway port/TLS and security option combinations. `TestGenerateCephXUser` checks Rook deployment-name to Ceph client-name conversion. `Test_clusterConfig_generateMonConfigOptions` validates default RGW monitor config, multisite sync disabling, `RgwConfig` overrides, and that `RgwCommandFlags` do not leak into mon config. `TestRgwConfigFromSecret` verifies secret lookup, missing-secret failure, and key extraction.

## Control Flow, State, and Persistence
The tests use fake clients and in-memory objects. `TestRgwConfigFromSecret` creates a Kubernetes Secret in the fake clientset and confirms `generateMonConfigOptions()` reads it. Most tests are table-driven transformations with no persisted state beyond fake API objects.

## Dependencies and Integration Points
The test suite depends on Ceph API types, fake Kubernetes clients, Rook test helpers, `stretchr/testify`, and pointer helpers. It indirectly guards deployment and mon-store behavior by asserting exact strings and maps generated from CRD specs.

## Risks and Test Signals
Strong signals include exact expected beast frontend strings, default-disabled legacy TLS versions, correct SDN internal port substitution, and secret-backed RGW config behavior. Gaps include Keystone secret mapping tests, keyring rotation errors, `RgwConfigFromSecret` invalid selector validation, and integration-level confirmation that Ceph accepts the produced option strings.
