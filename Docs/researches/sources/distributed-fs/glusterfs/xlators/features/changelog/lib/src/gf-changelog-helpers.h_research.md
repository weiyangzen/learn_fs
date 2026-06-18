# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-helpers.h

Purpose: this header declares changelog library helper types, connection/event structures, constants for journal subdirectories, callback invocation macros, and helper function prototypes.

Important types and APIs: `read_line_t` backs buffered line reads. `gf_event_list` stores ordered event queue state with `next_seq`, a mutex/cond, invoker thread, and queued events. `gf_event` stores a sequence number and flexible iovec payload. `gf_changelog_conn_state_t` describes pending, accepted, and disconnected states. `gf_changelog_t` is the per-brick connection object, holding brick path, RPC handles, notify filter, lifecycle callbacks, owner private data, invoker xlator, ordering flag, queue/pick callbacks, and event list. `gf_private_t` stores global library private state with connection and cleanup lists.

Control flow helpers: `gf_changelog_filter_check` tests whether an event matches a brick's notification filter. `GF_NEED_ORDERED_EVENTS` checks the ordered flag. `GF_CHANGELOG_INVOKE_CBK` switches `THIS` to the consumer xlator before invoking callbacks, then restores it. `SAVE_THIS` and `RESTORE_THIS` support similar context management.

State and persistence behavior: constants define `.current`, `.processed`, `.processing`, `.history`, and tracker names used by journal management. The header does not persist state itself but names directories and structures that the API and journal handlers maintain.

Dependencies and integration points: includes locking, xlator, changelog RPC common, and changelog journal headers. It is a central internal contract for changelog processing, RPC connection handling, ordered event delivery, and API access.

Risks: the callback macro references `entry` implicitly, so call sites must have the expected variable in scope. Event allocation macros require correct count/length accounting to avoid iovec payload corruption. Ordered event logic depends on `next_seq` bootstrap and queue/pick callbacks being paired correctly.

Test signals: ordered and unordered event queue/pick behavior, callback invocation with `THIS` restoration, filter matching, connection state transitions, event allocation sizing, and API pointer retrieval from `gf_private_t`.
