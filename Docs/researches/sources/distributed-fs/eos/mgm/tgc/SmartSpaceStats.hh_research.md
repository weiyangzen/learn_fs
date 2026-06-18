# sources/distributed-fs/eos/mgm/tgc/SmartSpaceStats.hh

## Purpose
`SmartSpaceStats.hh` declares the per-space statistics helper used by tape-GC workers. It combines MGM space stats, optional external script values, and locally tracked freed-byte history.

## Important APIs, Types, And Functions
The class exposes constructor `SmartSpaceStats(spaceName, mgm, config)`, `diskReplicaQueuedForDeletion()`, enum `Src`, `srcToStr()`, struct `SpaceStatsAndAvailBytesSrc`, `get()`, and `getQueryTimestamp()`. Private members include `AsyncUint64ShellCmd`, space name, MGM reference, mutex, query timestamp, stats payload, `RealClock`, `FreedBytesHistogram`, and cached config reference.

## Control Flow
The public contract is polling-oriented. GC logic calls `get()` for current stats and calls `diskReplicaQueuedForDeletion()` after queuing an eviction so future stats reflect pending local frees.

## State And Persistence
State is protected by `m_mutex`. `m_clock` is intentionally declared before `m_freedBytesHistogram` so the histogram's clock reference remains valid during construction and destruction.

## Dependencies And Integration Points
The header ties together the tape-GC config, MGM abstraction, async shell runner, histogram, and basic `SpaceStats`. `TapeGcStats` reports the `SpaceStats` result from this component.

## Risks And Edge Cases
The config cache reference must outlive `SmartSpaceStats`. The class serializes stats reads and freed-byte notifications under one mutex, so slow `get()` refreshes can block deletion notifications. The source enum is valuable for diagnostics and should remain synchronized with switch handling.

## Test Signals
Tests should validate each `Src` value, query timestamp updates, config cache lifetime/use, freed-byte notification effects, and behavior with dummy MGM/script outputs.
