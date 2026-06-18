# sources/distributed-fs/ceph/src/rgw/rgw_period_history.h

## Purpose
`rgw_period_history.h` declares `RGWPeriodHistory`, the abstraction that lets multisite code traverse a connected period history around the realm's current period while hiding storage/pull details behind a `Puller`.

## Important APIs, Types, And Functions
`RGWPeriodHistory::Puller` declares `pull()` for retrieving periods by id. `RGWPeriodHistory::Cursor` represents a valid position in connected history and exposes `get_error()`, bool conversion, `get_epoch()`, `get_period()`, `has_prev()`, `has_next()`, `prev()`, and `next()`. Top-level APIs are constructor, destructor, `get_current()`, `attach()`, `insert()`, and `lookup()`.

## Control Flow
The header documents the key contract: only periods connected to `current_period` are reachable through a valid cursor. `attach()` may fetch missing periods; `insert()` does not fetch; `lookup()` succeeds only inside current history.

## State And Persistence
The public class owns a private `Impl`. Cursor state stores a history pointer, mutex pointer, epoch, and optional error code. No durable state is stored by the header; persistence depends on the `Puller`.

## Dependencies And Integration Points
It depends on `RGWPeriod`, `optional_yield`, `DoutPrefixProvider`, `rgw::sal::ConfigStore`, boost intrusive forward declarations, and Ceph epoch types. `RGWPeriodPuller` implements the `Puller` interface.

## Risks And Test Signals
Risks are mostly contract misuse: holding cursors from disconnected histories, using default/error cursors, or assuming `insert()` fetches predecessors. Unit tests should validate cursor bool/error behavior, traversal boundaries, attach versus insert semantics, and mock-puller failure propagation.
