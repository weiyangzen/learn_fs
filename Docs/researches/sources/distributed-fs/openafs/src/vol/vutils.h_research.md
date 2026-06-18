# sources/distributed-fs/openafs/src/vol/vutils.h

## Purpose
Defines small common constants for volume utility programs.

## Important APIs And Constants
`VUTIL_TIMEOUT` sets a 15-second remote host timeout. `VUTIL_RESTART` and `VUTIL_ABORT` provide utility exit-code conventions aligned with `tcp/exits.h` comments.

## Control Flow, State, And Persistence
This header has no control flow and no persistent state. Its values are compile-time integration points for utilities that need common timeout and restart/abort signaling.

## Dependencies And Integration
It has only an include guard and no direct includes. Consumers are expected to include it where remote volume utility command behavior needs standardized timing and process-exit semantics.

## Risks And Test Signals
Risk is low, but changing exit codes can break scripts or supervising jobs. Test signals are mostly build coverage and utility-level tests that verify restartable vs non-restartable failures use the expected exit status.
