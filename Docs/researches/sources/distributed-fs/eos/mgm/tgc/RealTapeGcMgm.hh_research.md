# sources/distributed-fs/eos/mgm/tgc/RealTapeGcMgm.hh

## Purpose
`RealTapeGcMgm.hh` declares the production `ITapeGcMgm` implementation backed by a live `XrdMgmOfs`.

## Important APIs, Types, And Functions
The class overrides all MGM interface methods for config, stats, file size, namespace state, eviction, FSID mapping, replica scanning, and shell stdout. Private helpers read string and uint64 space config members and enumerate spaces.

## Control Flow
The header-level contract maps each abstract operation to a real MGM operation. It deletes copy/move operations because it holds an OFS reference and represents a live service adapter.

## State And Persistence
Only `m_ofs` is stored. The adapter reads and mutates external MGM state through referenced services but does not own persistent state.

## Dependencies And Integration Points
It depends on `XrdMgmOfs`, namespace file metadata, and `ITapeGcMgm`. `XrdMgmOfs` creates it and passes it to `MultiSpaceTapeGc`.

## Risks And Edge Cases
Lifetime of the referenced OFS must exceed the adapter and all tape-GC objects using it. The static config helpers are `noexcept` and default on all failures, which is operationally forgiving but less visible.

## Test Signals
Build tests should verify overrides match the interface. Integration tests should use a controlled MGM/FsView fixture or substitute `DummyTapeGcMgm` for unit-level logic.
