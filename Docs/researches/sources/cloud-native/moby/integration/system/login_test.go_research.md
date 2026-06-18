# sources/cloud-native/moby/integration/system/login_test.go

## Purpose
Verifies registry login with known bad credentials fails with an unauthorized error that includes the default registry endpoint.

## Important APIs, Types, And Functions
- `TestLoginFailsWithBadCredentials` checks `requirement.HasHubConnectivity`, calls `RegistryLogin`, and asserts error substrings.

## Control Flow
The test skips if Docker Hub connectivity is unavailable, then uses the environment API client to attempt login with `no-user`/`no-password`.

## State And Persistence
No successful auth state is created. A failed remote registry request may create transient network activity only.

## Dependencies And Integration Points
Depends on internet connectivity to Docker Hub, registry package default host, and daemon registry login API.

## Risks And Edge Cases
High external dependency risk: network, Hub availability, auth message changes, or rate limiting can affect the test. It is guarded by a connectivity requirement but still depends on remote error text.

## Test Signals
Expected error contains `unauthorized: incorrect username or password` and the default registry `/v2/` URL.
