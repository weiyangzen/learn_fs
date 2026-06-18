# sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.h

## Purpose

`scrub_resources.h` declares `ScrubResources` and `LocalResourceWrapper`, the local OSD resource bookkeeper used to limit concurrent primary scrub operations.

## Important APIs, types, and functions

- `log_upwards_t` is a simple callback for owner-level logging.
- `ScrubResources` owns `scrubs_local`, `resource_lock`, logging callback, and config reference.
- `can_inc_scrubs()` reports whether a regular local scrub can start.
- `inc_scrubs_local()` attempts to reserve a local primary scrub slot and returns a unique RAII wrapper on success.
- `dec_scrubs_local()` releases one slot.
- `dump_scrub_reservations()` reports local state to a formatter.
- `LocalResourceWrapper` represents an acquired slot and releases it in its destructor.

## Control flow

The OSD scheduler or `PgScrubber` attempts to acquire a local resource before starting a primary scrub. The returned `unique_ptr<LocalResourceWrapper>` is held for the active scrub session. When the session ends or aborts, destruction returns the count.

## State and persistence behavior

State is process-local and protected by a Ceph mutex. `scrubs_local` may exceed the configured limit only due to high-priority acquisitions. No persistent disk or cluster state is written.

## Dependencies and integration points

The header depends on `ceph_mutex`, `config_proxy`, `Formatter`, `osd_types`, and standard functional/string headers. It is part of OSD scrub scheduling/resource enforcement.

## Risks

The destructor-based release model requires strict ownership. Moving/destroying wrappers at unexpected times changes concurrency accounting. The config reference must outlive the resource object. Callers must not call `dec_scrubs_local()` manually for a wrapper they still own.

## Test signals

Tests should check the RAII ownership contract, high-priority behavior above `osd_max_scrubs`, concurrent access under lock, and formatter output.
