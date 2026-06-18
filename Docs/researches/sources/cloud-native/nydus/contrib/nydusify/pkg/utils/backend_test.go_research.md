<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go

## Purpose

This test file verifies registry backend config derivation and runtime external backend config rewriting.

## Important APIs, Types, and Functions

`TestNewRegistryBackendConfig` checks host/repo extraction, proxy selection, skip-verify, and Docker auth encoding. `TestNewRegistryBackendConfigUsesHTTPSProxyFallback` covers HTTPS proxy fallback. `TestBuildExternalBackend` covers missing external config and normal rewrite.

## Control Flow

The tests set environment variables, create temporary Docker config directories, parse image references, call the utility functions, and inspect returned structs or rewritten JSON.

## State and Persistence Behavior

Tests write temporary Docker `config.json` and temporary external backend files. The rewrite test reads the modified file back into `backend.Backend`.

## Dependencies and Integration Points

The tests use `distribution/reference`, Docker auth format, `backend.Backend`, and `testify`. They demonstrate that the utility is intended to interoperate with standard Docker credential files.

## Risks and Test Signals

The tests validate the common path but leave malformed backend config, empty backend lists, environment override precedence, and preservation of existing backend fields uncovered.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/backend_test.go -->
