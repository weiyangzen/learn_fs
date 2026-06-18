# Research: sources/distributed-fs/ipfs-kubo/config/provide.go

Purpose: Defines the unified provide/reprovide configuration and strategy validation for announcing local content to routing systems.

Important APIs/types/functions: Defaults for strategy, Bloom false-positive rate, DHT intervals/workers/sweep/resume/offline/timeout. `ProvideStrategy` bit flags include all, pinned, roots, MFS, unique, and entities. `Provide`, `ProvideDHT`, `ParseProvideStrategy`, `MustParseProvideStrategy`, `ValidateProvideConfig`, and `ShouldProvideForStrategy` are the key APIs.

Control flow, state, and persistence: Strategy parsing splits on `+`, maps `flat` to `all`, rejects unknown and empty tokens, prevents `all` from combining with selective strategies, and requires `+unique/+entities` to combine with pinned and/or MFS but not roots. Validation also enforces Bloom FP minimum, DHT interval bounds and the explicit `Provide.Enabled` requirement when interval is zero, positive worker/connection/batch/timeout settings, and non-negative dedicated workers/offline delay. State persists in config; sweep provider resume may persist runtime provider state downstream when enabled.

Dependencies and integration points: Uses libp2p Amino DHT provider validity. `core/commands/add.go` and provider subsystems use strategy and Bloom settings for fast provide and reprovides.

Risks and test signals: Strategy grammar is operator-facing and affects content discoverability. Bloom FP rates trade memory for skipped CID risk. Interval zero semantics changed and are guarded by validation. `provide_test.go` covers strategy parsing, validation edges, and `ShouldProvideForStrategy`.
