# sources/distributed-fs/coda/coda-src/venus/sighand.cc

## Purpose
This file implements Venus signal setup and signal-triggered control actions: clean termination, control-file command processing, log/stat toggles, fatal-signal zombie state, mount completion notification, and ASR child cleanup.

## Important APIs, Types, and Functions
`SigInit()` installs handlers and moves Venus into its own process group. `SigControl()` reads `VenusControlFile` on `SIGHUP` and handles `DEBUG`, `SWAPLOGS`, `STATSINIT`, and `STATS` commands. `SigChoke()` records fatal signals, notifies mariner, closes worker mux state, and suspends with only termination signals unblocked. `SigExit()` sets `TerminateVenus`, flushes and terminates recovery, unmounts, and exits. `SigMounted()` calls `gogogo(parent_fd)` for daemonization synchronization. `SigASR()` handles `SIGCHLD` for ASR launcher completion and unlocks the associated replicated volume.

## Control Flow
Startup calls `SigInit()` after logging/daemon infrastructure is ready. The main loop checks `TerminateVenus`, but `SigExit()` also performs immediate cleanup and exits from the handler. `SIGHUP` either swaps logs when no control file exists or executes the single command in the control file and unlinks it. Fatal signals enter a suspended zombie state for debugger attachment, then exit when interrupted or terminated. ASR child completion uses global `ASRpid`, `ASRfid`, and `VDB`.

## State and Persistence Behavior
Global state includes `TerminateVenus` and `mount_done`. Signal paths call recovery flushing/termination and VFS unmount, which affect persistent clean-shutdown markers. ASR cleanup mutates volume ASR state by clearing process group and unlocking.

## Dependencies and Integration Points
It integrates with recovery (`RecovFlush`, `RecovTerminate`), volume database, worker mux handling, daemonizer parent notification, Venus logging/stat functions, mariner, and ASR globals from `venus.private.h`.

## Risks and Test Signals
Many handler paths are not async-signal-safe because they use stdio, allocation-adjacent helpers, and complex subsystem calls. Tests should focus on integration behavior: `SIGHUP` control commands, SIGTERM clean shutdown marker, fatal signal debug state, ASR child unlock, and daemonization mount-complete notification.
