# sources/distributed-fs/eos/mgm/tgc/SpaceStats.hh

## Purpose
`SpaceStats.hh` defines the minimal statistics snapshot for an EOS space used by tape-aware garbage collection.

## Important APIs, Types, And Functions
`struct SpaceStats` contains `totalBytes`, `availBytes`, a default constructor initializing both to zero, and equality operator `operator==`.

## Control Flow
There is no complex control flow. Instances are filled by MGM adapters, modified by `SmartSpaceStats`, and copied into `TapeGcStats`.

## State And Persistence
The struct is a transient value object and does not persist anything itself.

## Dependencies And Integration Points
It is used by `ITapeGcMgm`, `RealTapeGcMgm`, `DummyTapeGcMgm`, `SmartSpaceStats`, and admin statistics output.

## Risks And Edge Cases
Only total and available bytes are tracked; used bytes or source timestamps must be derived elsewhere. Zero is both the default and a valid possible value, so consumers need separate error/source information when distinguishing missing data.

## Test Signals
Tests should cover default construction, equality, production stats scaling, dummy stats injection, and `SmartSpaceStats` augmentation of `availBytes`.
