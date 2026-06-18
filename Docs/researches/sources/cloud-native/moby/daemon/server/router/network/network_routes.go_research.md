# sources/cloud-native/moby/daemon/server/router/network/network_routes.go

## Purpose
`network_routes.go` implements network API handlers for list, inspect, create, connect, disconnect, delete, and prune across local and swarm scopes.

## Important APIs, Types, And Functions
Handlers include `getNetworksList`, `getNetwork`, `postNetworkCreate`, `postNetworkConnect`, `postNetworkDisconnect`, `deleteNetwork`, and `postNetworkPrune`. Helpers/errors include `invalidRequestError`, `ambiguousResultsError`, and `findUniqueNetwork`.

## Control Flow
List parses filters and merges swarm plus local results, using old `network.Inspect` responses before API 1.28 and `network.Summary` afterward. Inspect searches local full ID, full name, partial ID, then cluster network data and merges status for API 1.52+. Create rejects swarm duplicate names, strips `EnableIPv4` before API 1.48, validates locally, and redirects swarm-scoped creation to the cluster backend on `ManagerRedirectError`. Connect strips endpoint MAC before API 1.54. Delete resolves a unique network then dispatches to local or swarm removal.

## State And Persistence
Persistent changes are delegated to backends: network creation/removal, container endpoint attach/detach, and prune. The router only resolves targets and normalizes options.

## Dependencies And Integration Points
Depends on daemon filters, libnetwork errors/scope, local backend list config, cluster backend methods, API network types, and API-version helpers.

## Risks
Ambiguous names and partial IDs across local and swarm scopes are high-risk. Ignoring cluster errors in some list paths can hide manager problems. Version-gated fields such as `EnableIPv4`, status, and endpoint MAC must stay aligned with API docs.

## Test Signals
Network route behavior is mainly integration-tested; local unit coverage is absent in this file.
