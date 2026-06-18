<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth.go -->
# sources/cloud-native/moby/daemon/pkg/registry/auth.go

## Purpose
Implements registry credential stores, v2 login validation, authenticated HTTP client construction, credential-key normalization, and v2 registry ping/challenge discovery.

## Important APIs, Types, And Functions
`AuthClientID`, `loginCredentialStore`, `staticCredentialStore`, `NewStaticCredentialStore`, `loginV2`, `v2AuthHTTPClient`, `ConvertToHostname`, `resolveAuthConfig`, `PingResponseError`, and `PingV2Registry`.

## Control Flow
Login pings `/v2/`, builds token/basic auth handlers from challenges, sends a GET, and returns a captured identity token on 200. Auth resolution first checks the canonical config key, then scans legacy URL keys normalized to host. `PingV2Registry` records auth challenges from a registry response.

## State, Dependencies, And Integration Points
`loginCredentialStore` mutates a copy of auth config to capture refresh tokens; static store is read-only. Depends on Docker distribution auth/transport, registry API types, and transport headers.

## Risks And Test Signals
Authentication errors are translated for API classification. Legacy credential matching is compatibility-sensitive. `auth_test.go` covers official/private and full-URL credential resolution.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/registry/auth.go -->
