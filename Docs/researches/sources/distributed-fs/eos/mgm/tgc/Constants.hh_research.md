# sources/distributed-fs/eos/mgm/tgc/Constants.hh

## Purpose
`Constants.hh` centralizes tape-aware garbage-collector defaults, limits, and EOS space configuration member names.

## Important APIs, Types, And Functions
Constants include config cache age, freed-byte histogram bin limits and defaults, query-period name and limits, target available bytes name/default, optional free-byte script name/default, and total-bytes name/default. Notable names are `TGC_NAME_QRY_PERIOD_SECS`, `TGC_NAME_AVAIL_BYTES`, `TGC_NAME_FREE_BYTES_SCRIPT`, and `TGC_NAME_TOTAL_BYTES`.

## Control Flow
There is no executable control flow. Other classes use these constants for constructor defaults, validation, config lookup, logging, and error messages.

## State And Persistence
No runtime state is owned. The string constants define the persisted EOS space configuration keys used by `FsSpace` config and admin commands.

## Dependencies And Integration Points
`SpaceConfig`, `FreedBytesHistogram`, `SmartSpaceStats`, `RealTapeGcMgm`, `FsView`, `DevicesCmd`, and `SpaceCmd` use these values. Defaults are written into space config in FsView initialization when missing.

## Risks And Edge Cases
`TGC_DEFAULT_TOTAL_BYTES` is set to 1 exabyte, effectively preventing GC until configured for real deployments. Query-period maximum is derived from histogram depth and max bin width; changes must stay consistent with histogram validation. The comment says "tape-ware" in one place, but the values are functional.

## Test Signals
Tests should assert default `SpaceConfig` values, admin validation of recognized keys, histogram limit enforcement, and behavior when query period approaches maximum allowed depth.
