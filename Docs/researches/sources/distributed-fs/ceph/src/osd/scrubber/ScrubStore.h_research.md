# sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.h

## Purpose
Declares `Scrub::Store`, the scrubber-owned abstraction for staging, persisting, clearing, and listing known scrub errors.

## APIs and Control Flow
Public methods add object/snap errors, check staged emptiness, flush to a transaction, clean up backing objects, reinitialize for shallow/deep sessions, and return encoded object/snap errors. `at_level_t` bundles one DB object, `OSDriver`, `MapCacher`, and staged results. Private helpers clear OMAP, collect one DB, and merge shallow/deep encoded object wrappers.

## State, Dependencies, and Integration
State includes a `PgScrubber&`, `ObjectStore&`, collection id, current scrub level, and optional shallow/deep DB machinery. It integrates with object-store transactions, SnapMapper's `OSDriver`, `MapCacher`, admin scrub-ls APIs, and scrub backend persistence.

## Risks and Test Signals
Implementation paths assume DB optionals exist after construction and that lifecycle calls receive valid transactions. Encoded bufferlist compatibility is part of the external contract. Tests should validate construction, reinit semantics, empty/flush behavior, cleanup, and object/snap listing.
