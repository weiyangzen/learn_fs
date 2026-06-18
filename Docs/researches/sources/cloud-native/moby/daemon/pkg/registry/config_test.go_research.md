<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config_test.go -->
# sources/cloud-native/moby/daemon/pkg/registry/config_test.go

## Purpose
Tests daemon registry configuration validation for mirrors, insecure registries, service options, and index names.

## Important APIs, Types, And Functions
`TestValidateMirror`, `TestLoadInsecureRegistries`, `TestNewServiceConfig`, `TestValidateIndexName`, and `TestValidateIndexNameWithError` cover the major public/internal validation paths.

## Control Flow
The mirror table checks normalization and exact invalid-URI errors. Insecure registry tests call `loadInsecureRegistries` and inspect index config entries or invalid-argument classification. Service config tests combine mirror and insecure options. Index-name tests cover normalization and hyphen rejection.

## State, Dependencies, And Integration Points
No external state. It depends on containerd errdefs classification and protects daemon startup config validation.

## Risks And Test Signals
Exact URL parser error strings may be brittle. The suite has good coverage for schemes, credentials, fragments, ports, IPv6 forms, and Docker Hub normalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/config_test.go -->
