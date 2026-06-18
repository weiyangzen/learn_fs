# sources/distributed-fs/ceph/src/osd/scrubber/scrub_resources.cc

## Purpose

`scrub_resources.cc` implements local OSD scrub concurrency accounting. It enforces `osd_max_scrubs` for primary scrub sessions, allows high-priority scrubs to bypass the limit, logs counter changes, exposes dump output, and uses RAII to release local resources.

## Important APIs, types, and functions

- `ScrubResources::ScrubResources()` stores an upward logging callback and config proxy.
- `can_inc_scrubs()` checks the local primary scrub counter under lock.
- `inc_scrubs_local(bool is_high_priority)` increments the counter and returns a `LocalResourceWrapper` if high priority or below limit; otherwise returns `nullptr`.
- `can_inc_local_scrubs_unlocked()` compares `scrubs_local` to `conf->osd_max_scrubs` and logs denial.
- `dec_scrubs_local()` decrements under lock and asserts the counter remains non-negative.
- `dump_scrub_reservations()` emits current local count and configured max.
- `LocalResourceWrapper` destructor calls back to `dec_scrubs_local()`.

## Control flow

Scrub start code asks `inc_scrubs_local()` for a resource wrapper. If it receives `nullptr`, regular scrub initiation is delayed. If it receives a wrapper, the PG owns that wrapper for the scrub lifetime. Destruction of the wrapper releases the local slot. High-priority scrubs always increment, so the counter may exceed `osd_max_scrubs`; this blocks later regular scrubs until the count drops.

## State and persistence behavior

State is a single in-memory `scrubs_local` counter protected by `ceph::mutex`. There is no durable persistence. The local resource wrapper encodes ownership and release with RAII.

## Dependencies and integration points

The implementation depends on Ceph mutexes, config proxy, `Formatter`, `fmt`, Ceph assertions, and an owner-provided log callback. It integrates with OSD scrub scheduling/start code rather than the replica remote reservation protocol.

## Risks

Leaking a `LocalResourceWrapper` or failing to keep it for the full scrub lifetime skews concurrency. High-priority bypass can exceed configured limits by design, so callers must correctly classify priority. `dec_scrubs_local()` asserts non-negative; double-release is fatal. All counter accesses must remain under `resource_lock`.

## Test signals

Tests should cover below-limit acquisition, at-limit denial, high-priority bypass, RAII decrement on destruction, double-release prevention, dump formatting, and threaded acquisition/release contention.
