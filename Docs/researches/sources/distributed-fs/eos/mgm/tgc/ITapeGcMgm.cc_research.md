# sources/distributed-fs/eos/mgm/tgc/ITapeGcMgm.cc

## Purpose
`ITapeGcMgm.cc` defines the pure virtual destructor for the tape-GC MGM interface.

## Important APIs, Types, And Functions
The file implements `ITapeGcMgm::~ITapeGcMgm()`.

## Control Flow
There is no operational flow. The definition makes the abstract base class safely destructible through base pointers.

## State And Persistence
No state is owned or persisted.

## Dependencies And Integration Points
This destructor supports both `RealTapeGcMgm` and `DummyTapeGcMgm` implementations and any test mocks.

## Risks And Edge Cases
Missing this object file from a target would cause link failures. The destructor is empty and does not clean resources; derived classes own their cleanup.

## Test Signals
Compile/link tests deleting derived MGM adapters through `ITapeGcMgm*` are sufficient.
