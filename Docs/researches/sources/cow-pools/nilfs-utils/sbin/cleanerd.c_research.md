# File Research: sources/cow-pools/nilfs-utils/sbin/cleanerd.c

## Scope

Implements `nilfs_cleanerd`, the NILFS garbage-collection daemon responsible for selecting reclaimable segments, invoking NILFS GC/reclaim operations, handling control commands, and coordinating daemon lifecycle.

## APIs And Behavior

- Command-line parsing supports config file, help/version, obsolete nofork, and protection-period override.
- Startup canonicalizes device/mount paths, daemonizes with double fork, opens syslog, adjusts OOM killer score, opens NILFS raw read-write GC-lock handle, creates checkpoint reverse mapper, loads config, and creates a POSIX message queue named from device identity.
- Signal handling uses `siglongjmp` for SIGTERM/SIGINT shutdown, SIGHUP reload, and SIGUSR1 debug dump.
- Cleaner control messages support get-status, run, suspend, resume, reload, stop, shutdown, and NACK unimplemented tune/wait commands.
- Automatic mode pauses/resumes based on clean segment thresholds plus reserved-segment allowance.
- Manual mode tracks remaining passes and segments, accepts per-run protection period, speed, interval, and reclaimable-block overrides.
- Segment selection scans segment usage records, filters reclaimable segments outside the protection time or with future timestamps, ranks by timestamp-derived importance, and picks the least important segments.
- Cleaning builds `nilfs_reclaim_params` with protection sequence, protection checkpoint, and minimum reclaimable blocks, calls `nilfs_xreclaim_segment()`, handles cleaned/deferred counts, falls back on ENOMEM by reducing batch size, and retries after shrinking the protected region when needed.
- The main loop alternates state checks, selection, cleaning, interval recalculation, signal handling, and `ppoll()`/message-queue waits.

## State And Dependencies

`struct nilfs_cleanerd` combines NILFS library handle, checkpoint reverse map, config, runtime mode flags, timing state, cleaner speed, message queues, client UUID, manual-run state, and job ID. Dependencies include `libnilfsgc`, `nilfs_cleaner` message definitions, POSIX mqueue, syslog, uuid, `nilfs_get_sustat()`, `nilfs_get_suinfo()`, `nilfs_xreclaim_segment()`, freeze/thaw/sync helpers, and `cnormap`.

## Risks And Invariants

The daemon has several state encodings in `running`: negative for manual suspend, zero idle, one automatic running, two manual run. Correct cleaner restart/control depends on mount helpers preserving `gcpid`, `pp`, and `nogc` attributes. `nilfs_cleanerd_manual_resume()` sets `mm_prev_state = 0` before assigning `running`, so resume always returns to idle rather than the saved state. Message validation checks aggregate byte sizes but command-specific handlers still cast to extended request structures after validating their own argument length.
