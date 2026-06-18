# sources/distributed-fs/eos/mgm/tgc/DummyTapeGcMgm.cc

## Purpose
`DummyTapeGcMgm.cc` implements the test double for the tape-GC MGM interface. It supplies configurable space config/stats, canned shell stdout, simple success responses for namespace/eviction APIs, and call counters for unit-test assertions.

## Important APIs, Types, And Functions
Implemented methods include `getTapeGcSpaceConfig()`, `getSpaceStats()`, `getFileSizeBytes()`, `fileInNamespaceAndNotScheduledForDeletion()`, `evictAsRoot()`, `getFsIdToSpaceMap()`, `getSpaceToDiskReplicasMap()`, `getStdoutFromShellCmd()`, setters for config/stats/stdout, and getter methods for call counters.

## Control Flow
Most methods lock `m_mutex`, update a counter when relevant, and return either configured data or defaults. `getFileSizeBytes()` always returns 1 and `fileInNamespaceAndNotScheduledForDeletion()` always returns true. Replica-map and FS-ID map methods return empty maps, making multi-space population complete quickly in tests.

## State And Persistence
State is in-memory and protected by `m_mutex`: maps from space to config/stats, counters, and shell stdout. No production state is touched.

## Dependencies And Integration Points
The dummy implements `ITapeGcMgm` and is used by unit tests for `CachedValue`, `SmartSpaceStats`, `MultiSpaceTapeGc`, `SpaceToTapeGcMap`, and likely `TapeGc`.

## Risks And Edge Cases
Some methods catch all exceptions and return defaults, which is convenient for tests but can hide test setup errors. `getStdoutFromShellCmd()` ignores `cmdStr` and `maxLen`, so it does not test length limits or command-specific behavior. Empty replica maps mean population tests do not cover large namespace scans unless extended.

## Test Signals
Tests should assert call counters, default fallbacks, configured space stat/config retrieval, stdout injection for async script parsing, and behavior of components when maps are empty.
