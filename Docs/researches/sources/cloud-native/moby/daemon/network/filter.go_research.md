# sources/cloud-native/moby/daemon/network/filter.go

## Purpose
This file defines network list and prune filtering logic.

## Important APIs, Types, And Functions
`Filter` wraps `filters.Args` plus derived fields for dangling/use and until time. `FilterNetwork` abstracts the network data required for matching. Constructors are `NewFilter` and `NewPruneFilter`; matching helpers are `Matches`, `matchesUse`, `validateNetworkTypeFilter`, and `matchesType`.

## Control Flow
Constructors validate accepted filter keys, parse the optional single `dangling` boolean, validate `type` values, and parse a single `until` timestamp. Prune filters implicitly require dangling-only results. `Matches` applies driver, name, id, label, negative label, scope, use/dangling, type, and until checks in sequence.

## State, Persistence, And Dependencies
The filter is immutable after construction except for the exported `IDAlsoMatchesName` compatibility flag. There is no persistence. Dependencies include internal `filters`, timestamp parsing, errdefs, and predefined network detection.

## Integration Points
Daemon network list and prune flows pass libnetwork-backed values through this filter. The interface keeps filter matching decoupled from concrete libnetwork types.

## Risks And Edge Cases
`dangling` and `until` allow only one value. Network `type=builtin` maps to predefined names, while `custom` means not predefined. The `IDAlsoMatchesName` flag lets id filters also match names for compatibility and can broaden results substantially.

## Test Signals
`filter_test.go` exercises accepted/rejected filters, dangling semantics, label and negative label behavior, type/scope/name/id matching, prune restrictions, ID/name overlap, and until timestamp cutoffs.
