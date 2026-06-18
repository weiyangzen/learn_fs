# sources/distributed-fs/eos/mgm/tgc/SpaceConfig.hh

## Purpose
`SpaceConfig.hh` defines the configuration values for a tape-aware garbage collector managing one EOS space.

## Important APIs, Types, And Functions
`struct SpaceConfig` contains `queryPeriodSecs`, `availBytes`, `freeBytesScript`, and `totalBytes`. Its default constructor initializes fields from `Constants.hh`.

## Control Flow
There is no behavior beyond default construction. `RealTapeGcMgm` populates instances from space config; tests and dummy MGM can inject custom instances.

## State And Persistence
The struct is a value snapshot of persisted EOS space config keys. It does not persist changes itself.

## Dependencies And Integration Points
It is returned by `ITapeGcMgm::getTapeGcSpaceConfig()`, cached by `CachedValue`, read by `SmartSpaceStats`, and used by space-specific `TapeGc` workers to decide thresholds and query cadence.

## Risks And Edge Cases
Defaults are conservative: `availBytes` is zero and `totalBytes` is 1 exabyte. Invalid operational values are validated elsewhere rather than in this struct, so consumers must check ranges.

## Test Signals
Tests should assert default values, custom assignment, cache refresh behavior with this struct, and consumer validation for invalid periods or thresholds.
