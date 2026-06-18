<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c -->
# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c

## Purpose
Implements daemon-side bit-rot filesystem scrubbing: scheduled or on-demand traversal of child bricks, checksum verification against object signatures, marking corrupt objects, bad-object collection, scrub worker scaling, scrub option handling, and scrub monitor initialization.

## APIs, Types, and Functions
Major object-verification helpers are `bitd_fetch_signature()`, `bitd_scrub_pre_compute_check()`, `bitd_scrub_post_compute_check()`, `bitd_compare_ckum()`, and `br_scrubber_scrub_begin()`. Scanner/worker flow is handled by `br_fsscanner()`, `br_fsscanner_handle_entry()`, `wait_for_scrubbing()`, `br_scrubber_proc()`, queue helpers, and cleanup handlers. Scheduling APIs include `br_fsscan_schedule()`, `br_fsscan_activate()`, `br_fsscan_reschedule()`, `br_fsscan_deactivate()`, and `br_fsscan_ondemand()`. Option APIs include `br_scrubber_handle_options()` and throttle/frequency helpers. Status and integration APIs include `br_child_set_scrub_state()`, `br_collect_bad_objects_from_children()`, `br_get_bad_objects_list()`, `br_monitor_thread()`, `br_scrubber_monitor_init()`, and `br_scrubber_init()`.

## Control Flow, State, and Persistence
The timer-wheel callback `br_kickstart_scanner()` resets stats, moves the monitor to active, and broadcasts a kick to per-child scanner threads. Each scanner walks its child with `syncop_ftw()`, batches entries into `br_scanfs.queued`, swaps queued entries to ready, and wakes scrubber workers. Workers round-robin across children, run lookup/open, skip non-regular and DHT linkfiles, fetch signature/version before checksum, compute SHA256, refetch signature after checksum to avoid races, compare hashes, and set `BITROT_OBJECT_BAD_KEY` plus `EVENT_BITROT_BAD_FILE` on mismatch. Monitor state, child active flags, queues, timer, worker count, and scrub stats are in `br_private_t`, `br_child_t`, `br_scanfs`, `br_scrubber`, and `br_monitor`; persistent effects are xattrs on corrupted objects and quarantine/bad-object directory contents read through child translators.

## Dependencies and Integration
Depends on GlusterFS syncop lookup/open/readdir/fgetxattr/fsetxattr/ftw, inode/fd/loc helpers, timer-wheel, changelog-era bit-rot signature xattrs, SHA256 checksum helpers, pthreads, token-bucket initialization, event reporting, message IDs, and state-machine functions in `bit-rot-ssm.c`. It is initialized and driven by the main bit-rot translator in `bit-rot.c`.

## Risks and Test Signals
Risks include races with concurrent signing or writes despite pre/post checks, cancellation while worker owns queued entries, scanner/worker deadlocks around condition variables, memory pressure in copied entries and signatures, bad-object marking failure after mismatch detection, shard-stat exceptions hiding counts, and zero-timeout bugs for stalled/invalid frequency. Test signals are scrub scheduling/rescheduling/ondemand, pause/resume, connected/disconnected child handling, checksum mismatch marking and event emission, unsigned/stale signature counts, bad-object list aggregation, worker scale up/down by throttle, and long-running cancellation/cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/bitd/bit-rot-scrub.c -->
