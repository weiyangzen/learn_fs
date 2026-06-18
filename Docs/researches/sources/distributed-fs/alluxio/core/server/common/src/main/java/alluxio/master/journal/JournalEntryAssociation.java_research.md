# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalEntryAssociation.java

## Purpose
`JournalEntryAssociation` maps a polymorphic journal entry protobuf to the master service responsible for applying it.

## Important APIs, Types, And Functions
`getMasterForEntry` checks `has*` fields on `JournalEntry` and returns file system, block, meta, or table master constants.

## Control Flow, State, Dependencies, Risks, And Tests
The method is a deterministic classifier with no state or persistence. It is used by backup restore and any replay path needing to route entries. Dependencies are `Constants` and generated journal protobuf accessors. Risks are new journal entry types not being added, ambiguous entries with multiple fields being classified by first matching group, and restore fatal failures on unknown entries. Tests should cover every journal entry variant, unknown/default entry rejection, and ordering if multi-field entries can be constructed.
