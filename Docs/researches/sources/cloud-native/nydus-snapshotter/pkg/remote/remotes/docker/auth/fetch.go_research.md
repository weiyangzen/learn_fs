# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/fetch.go

This file is copied from containerd auth logic and implements token option generation plus GET/POST token fetching. `GenerateTokenOptions` converts a parsed Bearer challenge into `TokenOptions`, requiring a valid `realm`, copying service, username, secret, and splitting scope by spaces when present.

`FetchTokenWithOAuth` sends an OAuth-style form POST using password or refresh-token grant depending on username, optionally asks for offline access, merges caller headers, sets a default containerd user agent, checks HTTP status, decodes `OAuthTokenResponse`, and requires an access token. `FetchToken` sends a GET token request, adds service/scope query parameters, uses HTTP basic auth when a secret is present, optionally sets `offline_token=true`, decodes `FetchTokenResponse`, canonicalizes `access_token` into `token`, and requires a token.

State is remote auth server response data; no persistence. Integration points include Docker authorizer/resolver code, challenge parsing, registry auth flows, and containerd version. Risks include scope splitting producing `[""]` when an empty scope parameter exists, error handling depending on response bodies, refresh-token grant choice when username is empty, and no direct tests for HTTP fetch functions in this subset.
