# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot.h

Purpose: this header defines the shared daemon-side data structures and helper declarations used by bit-rot signer and scrubber code. It bridges GlusterFS logging, dict, syncop, changelog, timer wheel, throttle, common bitrot xattr formats, and scrub status/state-machine headers.

Important types and APIs: `scrub_throttle_t` and `scrub_freq_t` enumerate runtime scrub policy values. `br_child_t` stores per-brick state: connection status, child xlator, inode table, brick path, worker thread, timer pool, scanner queues, and active scrub flag. `br_private_t` is the top-level xlator private state containing child arrays, event queues, signer object queues, timer wheel, token bucket, scrub stats, `br_scrubber`, and `br_monitor`. `br_object_t` carries a GFID, signed version, sign state, and target child for queued signing. Exported helpers include `br_log_object`, `br_calculate_obj_checksum`, `br_prepare_loc`, `bitd_is_bad_file`, and `br_get_bad_objects_list`.

Control flow model: the types encode three cooperating loops: child connection event handling through `br_private.bricks`, signer object processing through `br_obj_n_workers.objects` plus `object_cond`, and scrub scanning through `br_scanfs` and `br_scrubber.scrublist`. Inline helpers define state transitions and checks for connected, failed, witnessed, and scrub-active children.

State and persistence behavior: this header does not persist state directly, but it defines the in-memory state that coordinates persistent xattr operations performed in the daemon and stub. `br_monitor` stores scrub scheduling state and timer pointer, while `br_private.expiry_time` and `signer_th_count` reflect volume options that shape when persistent signatures are written.

Dependencies and integration points: consumers must include the bit-rot common formats from the stub directory, scrub status, timer wheel, and changelog types. The header intentionally exposes enough daemon internals for scrub source files to update counters, build locs, detect bad objects, and drive scrub monitor events.

Risks: the header concentrates many mutexes and condition variables across nested structures, so implementation code must preserve documented lock order, especially around child locks and scrub monitor locks. Because `br_child_t.list` is reused in signer and scrubber lists, double insertion/removal bugs are a risk if mode checks regress.

Test signals: compile-time coverage should catch enum and function prototype drift. Runtime tests should exercise child state transitions, scrub pause/resume event derivation, status collection, and shared helper behavior when child inode tables or timer pools are missing.
