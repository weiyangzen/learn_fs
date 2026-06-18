# sources/cloud-native/moby/daemon/pkg/registry/search.go

## Purpose
Implements Docker registry search for repositories. This is a legacy V1 search path with local filtering for official status and stars, plus compatibility handling for the deprecated automated-build field.

## Important APIs, Types, And Functions
`Service.Search` validates filters and returns `[]registry.SearchResult`. `searchUnfiltered` resolves index information, builds a V1 endpoint, authorizes the HTTP client, and calls `searchRepositories`. `splitReposSearchTerm` separates registry host from repository term. `newIndexInfo` converts service config into `registry.IndexInfo`. `searchRepositories` sends `/v1/search?q=...&n=...` and decodes `registry.SearchResults`.

## Control Flow
Search rejects unknown filters, parses booleans, computes the highest requested stars threshold, short-circuits `is-automated=true` to no results, fetches unfiltered remote results, then applies local `is-official` and `stars` filtering while forcing `IsAutomated=false`. `searchUnfiltered` rejects schemes in repository names, treats Docker Hub library names specially, creates an endpoint, chooses a V2-authenticated client for identity-token auth, otherwise wraps the V1 auth transport, and performs the search request.

## State And Persistence
The service config is read under `s.mu.RLock`; no persistent config is mutated. Search result values are copied through the filtered slice with `IsAutomated` normalized.

## Dependencies And Integration Points
Depends on Docker API registry types, daemon filters, V1 endpoint creation, V1/V2 auth helpers, and containerd logging. It is reached by API search endpoints and relies on service registry configuration for mirrors, insecure registries, and TLS.

## Risks And Edge Cases
Search only supports V1 endpoints and rejects `/v2` endpoint strings. Filter behavior is partly client-side and can diverge from registry-side semantics. `limit` is constrained to 1..100, with 25 as default. Authentication path differs when both identity token and username are present.

## Test Signals
`search_test.go` covers successful search, invalid filters, deprecated automated filtering, stars and official filtering, error classification, and index-info construction for default, mirrored, and insecure configurations.
