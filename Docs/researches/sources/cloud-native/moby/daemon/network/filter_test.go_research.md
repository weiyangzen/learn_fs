# sources/cloud-native/moby/daemon/network/filter_test.go

## Purpose
This file tests daemon network filter behavior on non-Windows platforms.

## Important APIs, Types, And Functions
`mockFilterNetwork` implements `FilterNetwork`. `TestFilter` drives `NewFilter`, `NewPruneFilter`, and `Filter.Matches` through a table of built-in, custom, attached, labeled, and dated mock networks.

## Control Flow
Each case constructs filter args, chooses list or prune filter construction, optionally enables `IDAlsoMatchesName`, asserts expected construction errors, then collects matched network names and compares them to expected results.

## State, Persistence, And Dependencies
All state is local test data. Dependencies include Docker API network constants, internal filters, `time`, and gotest assertions.

## Integration Points
The tests encode API-visible behavior for `docker network ls --filter` and network prune filtering.

## Risks And Edge Cases
The test is build-tagged `!windows`, matching platform differences in predefined network semantics. The mock data intentionally uses ROT13-like IDs and overlapping names to expose `id` matching behavior.

## Test Signals
Coverage includes empty filters, exact driver/scope, builtin/custom type, invalid type, dangling true/false values and duplicates, labels and negative labels, invalid unsupported prune keys, relative/absolute until values, ID matching with/without name fallback, and prune's implicit dangling behavior.
