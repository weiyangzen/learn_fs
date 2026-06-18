# sources/distributed-fs/ceph/src/mon/MonmapMonitor.cc

## Purpose
`MonmapMonitor.cc` implements the Paxos-backed monitor-map service. It creates and commits monmap versions, loads committed maps, services monmap read commands, prepares mutating monitor commands, processes monitor join messages, applies persistent monitor feature bits, manages subscriptions, and coordinates stretch-mode monitor-map changes with `OSDMonitor`.

## Important APIs, Functions, and Types
The main lifecycle methods are `create_initial()`, `update_from_paxos()`, `create_pending()`, `encode_pending()`, and `on_active()`. `apply_mon_features()` updates persistent feature bits and `min_mon_release` after a full quorum agrees on support; `C_ApplyFeatures` retries that work once the service is writeable.

Query and update dispatch is split into `preprocess_query()`, `preprocess_command()`, `preprocess_join()`, `prepare_update()`, `prepare_command()`, and `prepare_join()`. Supported read commands include `mon stat`, `mon getmap`, `mon dump`, and `mon feature ls`. Mutating commands include `mon add`, `mon remove`/`mon rm`, `mon feature set`, `mon set-rank`, `mon set-addrs`, `mon set-weight`, `mon enable-msgr2`, election strategy changes, disallowed-leader add/remove, `mon set_location`, stretch tiebreaker changes, and stretch-mode enable/disable.

Stretch-mode logic is centralized in `try_enable_stretch_mode()` and static `validate_and_enable_stretch_mode()`, with emergency state helpers `trigger_degraded_stretch_mode()` and `trigger_healthy_stretch_mode()`. `get_monmap()`, `check_subs()`, `check_sub()`, `tick()`, `dump_info()`, and `should_propose()` fill out the service surface.

## Control Flow
Initial cluster creation copies the boot monmap, sets epoch 1, and records default persistent monitor features unless the debug override disables that. Normal loading asks Paxos for `get_last_committed()`, skips if the running `mon.monmap` is already current, optionally signals bootstrap, decodes the version into `mon.monmap`, erases the old `mkfs/monmap` key if present, updates subscribers, records `min_mon_release` metadata, and notifies the monitor about the new map.

For a pending proposal, `create_pending()` clones the committed monmap, increments epoch, updates `last_changed`, and clears `removed_ranks`. `encode_pending()` asserts epoch monotonicity, encodes with quorum connection features, stores the new version and last-committed marker, creates the first cluster fingerprint at epoch 1, and persists health checks generated from `pending_map`.

Read commands are answered during preprocessing when they can be satisfied from committed state. `mon getmap` and `mon dump` optionally decode historical versions from Paxos. Mutating commands run in `prepare_command()` against the committed `monmap` for validation and mutate only `pending_map`. The function explicitly documents that user replies must not claim a change is committed until the proposal finishes. Successful mutating commands call `wait_for_commit()` and return `true` so PaxosService proposes immediately; non-mutating/idempotent failures reply without proposing.

Monitor joins first pass `preprocess_join()`, which filters already-known joins, duplicate address/name cases, insufficient caps, and missing stretch locations. `prepare_join()` removes conflicting name/address entries from `pending_map`, adds the joining monitor, preserves existing location when appropriate, and updates `last_changed`.

Stretch-mode enablement plugs Paxos while it validates OSD pool/rule changes and monmap changes together. The monmap side validates that the CRUSH dividing bucket has exactly two data subtrees, every monitor has a location at that bucket type, monitors exist in both data zones, and the tiebreaker is exactly one monitor in a third location or an explicit valid monitor outside the data zones. Commit mode sets connectivity election, disallows the tiebreaker, records it, and enables stretch mode. OSDMonitor is then asked to propose its companion changes.

## State and Persistence
Persistent state is the encoded `MonMap` at each Paxos version plus service health checks. `monmap_bl` caches the currently loaded buffer, and `pending_map` holds uncommitted state during a proposal. `on_active()` also writes the local `Monitor::MONITOR_NAME/joined` marker once the daemon has been part of an active quorum. `update_from_paxos()` keeps `min_mon_release` as a side metadata file in the monitor store.

`should_propose()` always returns true with zero delay, so this service intentionally avoids batching and assumes only one pending mutation is handled at a time. Subscriptions track the next epoch a client wants; `check_sub()` sends the latest monmap and advances or removes the subscription.

## Dependencies and Integration Points
This implementation is tightly coupled to `Monitor`, `PaxosService`, `Paxos`, `MonMap`, monitor sessions/subscriptions, `MMonCommand`, `MMonJoin`, Ceph feature definitions, `OSDMonitor`, `CrushWrapper`, command parsing, and monitor logging. Stretch mode crosses service boundaries: monmap election/tiebreaker state and OSD pool/CRUSH state must be validated and proposed together.

## Risks
The command path depends on disciplined committed-vs-pending semantics. Returning success based on uncommitted pending state could mislead users if quorum is lost after a monitor add/remove. Several commands mutate `pending_map` without rechecking all races because immediate proposal delay is assumed; changes to `should_propose()` would require revisiting those assumptions. Stretch-mode validation dereferences `crush.get_validated_type_id(dividing_bucket)` and relies on the caller having already validated CRUSH type existence. The `set_new_tiebreaker` path parses `yes_i_really_mean_it` but does not appear to use it in the final guard.

Monitor add/remove can affect quorum availability, so reply wording and wait-for-commit behavior are important. Historical map reads allocate a temporary `MonMap` and must delete it on all success paths. Subscription removal uses session-map mutation and must not race with iteration assumptions.

## Test Signals
Tests should cover monmap encode/load across epochs, epoch-1 fingerprint behavior, mkfs monmap cleanup, feature application only under full quorum, all read command formats, add/remove duplicate name/address cases, msgr2 address expansion, election strategy and disallowed-leader invariants, join idempotency, stretch-mode validation for missing locations/wrong tiebreakers/wrong subtree counts, degraded/healthy stretch triggers, and subscription next-epoch updates.
