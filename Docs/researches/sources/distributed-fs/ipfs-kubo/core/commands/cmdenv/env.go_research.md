<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go

## Purpose

Centralizes command environment extraction, string escaping, and fast DHT providing helpers shared by command handlers.

## Important APIs, Types, and Functions

`GetNode`, `GetApi`, and `GetConfigRoot` extract Kubo node/API/config root from `commands.Context`. `EscNonPrint` and `needEscape` sanitize display strings. `ExecuteFastProvideRoot`, `ExecuteFastProvideDAG`, and `provideCIDSync` implement immediate DHT provide paths for import/add-like commands.

## Control Flow

`GetApi` honors `--offline` and deprecated `--local` by wrapping CoreAPI with `options.Api.Offline`. Fast root provide checks `Provide.Enabled`, active DHT availability, and `Provide.Strategy` match before either blocking on `router.Provide` or launching an async goroutine with node-lifetime context and timeout. Fast DAG provide builds a bloom tracker, walks entity roots or DAG links from the blockstore, and sends CIDs to a provider with backpressure.

## State and Persistence Behavior

Extraction functions are read-only. Fast provide mutates network/provider state by publishing provider records but does not alter blockstore data. Async goroutines are tied to `IpfsNode.Context()` to avoid outliving the daemon.

## Dependencies and Integration Points

Depends on Kubo `commands.Context`, CoreAPI options, config provide strategy logic, boxo blockstore/DAG walker, and libp2p routing. `ExecuteFastProvideDAG` integrates with node provider implementations and import/add workflows.

## Risks and Edge Cases

All extraction helpers type assert the environment and fail if used with an unexpected context. `provideCIDSync` assumes callers checked DHT availability. Async provide failures are logged rather than returned. Bloom tracker sizing and strategy flags affect how much of a DAG is announced.

## Test Signals

`env_test.go` covers string escaping only. Fast provide logic needs integration tests or fakes for strategy gating, DHT absence, wait vs async cancellation, and provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/cmdenv/env.go -->
