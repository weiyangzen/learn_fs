# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournaledGroup.java

## Purpose
`JournaledGroup` treats multiple `Journaled` components as one checkpointed/replayable component.

## Important APIs, Types, And Functions
It stores component list and group `CheckpointName`. `processJournalEntry` offers entries to components in order until one accepts. `resetState` resets components in reverse order. Checkpoint write/restore either runs component file checkpoint futures or uses compound checkpoint streams. Journal iterators are concatenated.

## Control Flow, State, Dependencies, Risks, And Tests
Persistence is a compound checkpoint or concatenated journal-entry stream representing all child components. Dependencies include `JournalUtils`, `CloseableIterator.concat`, Guava `Lists.reverse`, and checkpoint APIs. Risks include entries accepted by the wrong first component, component order being part of replay semantics, partial async checkpoint failures, and unknown compound checkpoint entries. Tests should cover ordering, reverse reset, checkpoint round trips, async future aggregation, iterator close behavior, and duplicate entry handlers.
