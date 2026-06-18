# Research: sources/distributed-fs/ipfs-kubo/config/types.go

Purpose: Provides custom JSON helper types used throughout config for flexible strings, ternary flags, priorities, optional durations/integers/strings/bytes, and removed-key sentinels.

Important APIs/types/functions: `Strings`, `Flag`, `ResolveBoolFromConfig`, `Priority`, `OptionalDuration`, `Duration`, `OptionalInteger`, `OptionalString`, `OptionalBytes`, and sentinel types `swarmLimits`, `experimentalAcceleratedDHTClient`, and `graphsyncEnabled`.

Control flow, state, and persistence: `Strings` decodes either a string or array and encodes nil/single/array shapes. `Flag` maps false/default/true to JSON false/null/true. `Priority` maps disabled/default/positive priorities and rejects invalid values. Optional types preserve omitted/default as nil and provide `WithDefault`. `OptionalBytes` validates/parses human byte strings and numeric values. Sentinel unmarshaler types accept limited empty/false forms and reject removed config keys with migration guidance.

Dependencies and integration points: Used by nearly every config section and by command code resolving config-vs-flag precedence. Depends on JSON, time, and `go-humanize`.

Risks and test signals: Several `WithDefault` methods tolerate nil receivers, which is intentional but easy to overlook. `OptionalBytes.WithDefault` panics if invalid values are manually constructed. Sentinel errors are important migration UX. `types_test.go` covers all major helper types and invalid cases.
