# sources/cloud-native/moby/daemon/internal/distribution/registry_unit_test.go

## Purpose
Tests registry bearer token pass-through behavior.

## APIs, Control Flow, and Integration
The test server handler validates `Authorization` against `Bearer mysecrettoken`. `testTokenPassThru` constructs a repository endpoint using `RegistryToken` and performs a blob stat for a dummy digest. `TestTokenPassThru` expects success against the token-checking server. `TestTokenPassThruDifferentHost` changes endpoint host to another registry and expects an error.

## State, Dependencies, and Risks
State is an HTTP test server. The tests validate that registry tokens are passed to the intended registry flow and not blindly reused for a mismatched host. They do not cover username/password token exchange or TLS fallback.
