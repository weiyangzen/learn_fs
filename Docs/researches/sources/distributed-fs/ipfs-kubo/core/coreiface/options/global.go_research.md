# sources/distributed-fs/ipfs-kubo/core/coreiface/options/global.go

## Purpose
Defines global CoreAPI view options for offline mode and block fetching.

## Important APIs, Types, and Functions
Defines `ApiSettings`, `ApiOption`, `ApiOptions`, `ApiOptionsTo`, `Api` option namespace, and methods `Offline` and `FetchBlocks`.

## Control Flow and State
Defaults are online API mode with block fetching enabled. Option functions mutate a settings struct in order. These settings are later interpreted by CoreAPI implementations to select offline/no-fetch behavior.

## Dependencies and Integration Points
No external dependencies. Used by `CoreAPI.WithOptions` and conformance tests for offline add/routing behavior.

## Risks and Test Signals
Risks include confusion between fully offline mode and fetch-blocks-disabled mode, and incomplete propagation to sub-APIs. Tests use `Api.Offline(true)` for local UnixFS add and offline routing put behavior.
