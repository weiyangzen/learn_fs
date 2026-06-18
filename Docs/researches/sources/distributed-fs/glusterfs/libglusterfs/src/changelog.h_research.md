# sources/distributed-fs/glusterfs/libglusterfs/src/changelog.h

## Purpose
`changelog.h` defines the public changelog consumer interface and event ABI used by GlusterFS components that register for brick changelog events. It is a header-only contract: it declares event types, event payload structures, callback signatures, brick subscription metadata, and the legacy and generic registration APIs.

## Important APIs, Types, And Functions
`CHANGELOG_EV_SELECTION_RANGE` defines the bit range used for event filtering. The event bit masks are `CHANGELOG_OP_TYPE_JOURNAL`, `OPEN`, `CREATE`, `RELEASE`, `BR_RELEASE`, and `CHANGELOG_OP_TYPE_MAX`.

Payload structures include `ev_open`, `ev_creat`, `ev_release`, `ev_release_br`, and `ev_changelog`. `changelog_event_t` carries `ev_type` plus a union of those payloads. `CHANGELOG_EV_SIZE` exposes the ABI size of a changelog event.

Callback typedefs define plugin hooks: `CALLBACK`, `INIT`, `FINI`, `CONNECT`, and `DISCONNECT`. `struct gf_brick_spec` describes one watched brick with `brick_path`, event `filter`, hook pointers, and an opaque `ptr`.

The legacy API is `gf_changelog_register`, `gf_changelog_scan`, `gf_changelog_start_fresh`, `gf_changelog_next_change`, and `gf_changelog_done`. The newer generic API is `gf_changelog_init` and `gf_changelog_register_generic`.

## Control Flow
Consumers initialize the changelog subsystem, register one or more bricks, scan for available changes, iterate paths with `gf_changelog_next_change`, and acknowledge processed changelog files with `gf_changelog_done`. Under the generic API, each brick spec can receive lifecycle callbacks for init/fini/connect/disconnect and per-event callbacks.

## State And Persistence Behavior
The header itself holds no state, but the API represents persistent changelog state: brick paths, scratch directories, changelog files, reconnect policy, event filters, and done/acknowledged changelog files. `ev_changelog.path` is a fixed `PATH_MAX` buffer, and event structures embed GFIDs and flags directly for stable handoff.

## Dependencies And Integration Points
The file forward-declares `struct gf_brick_spec` and relies on external definitions for `PATH_MAX`, `ssize_t`, and integer types through including translation units. It integrates with changelog libraries, bitrot stub release events, geo-replication or indexing consumers, and brick-level event delivery.

## Risks And Edge Cases
This is ABI-sensitive because `changelog_event_t` and `CHANGELOG_EV_SIZE` may be consumed across library boundaries. The comment says "Max bit shiter", indicating stale or typo-prone documentation. Event selection assumes no more than five bit positions unless the range is updated. Fixed-size path storage can truncate if producers are not careful. Callback typedefs use raw `void *` and `char *`, so ownership and lifetime must be documented by implementers.

## Test Signals
Tests should validate event filter bit masks, `CHANGELOG_EV_SIZE` stability where ABI matters, legacy scan/next/done flows, generic multi-brick registration, callback ordering on connect/disconnect/fini, path length handling, and logical release events from bitrot paths.
