# sources/distributed-fs/coda/coda-src/venus/venus.private.h

## Purpose
This private umbrella header defines Venus-wide constants, error codes, uid/gid/mode defaults, lock/timing/logging macros, utility declarations for source files without dedicated headers, and exported globals shared by many Venus modules.

## Important APIs, Types, and Functions
It defines replica-control rights, internal errors (`ESYNRESOLVE`, `EASYRESOLVE`, `ERETRY`, `EASRSTARTED`), default paths and minimum cache dimensions, special uids/gids, fid lookup flags, logging/timing macros, lock-level helpers, cache event/stat structures, string case macros, `CHOKE`, and `MRPC_common_params`. It declares many functions implemented in `venusutil.cc`, daemon helpers, `MUX_add_callback`, and globals from `venus.cc`, recovery, stats, and ASR state.

## Control Flow
The header has no runtime flow, but its macros shape control flow throughout Venus: `LOG` compiles away without `VENUSDEBUG`, `ObtainLock`/`ReleaseLock` dispatch by enum, `START_TIMING`/`END_TIMING` either measure or stub elapsed time, and `CHOKE` captures file/line for fatal handling.

## State and Persistence Behavior
It declares both transient process globals and structures that feed persistent behavior, such as `NullFid`, `NullVV`, `VFSStats`, `RPCOpStats`, cache sizing, ASR globals, and recovery-related configuration. It also defines `MRPC_common_params` used to pass multicast operation state.

## Dependencies and Integration Points
This is one of the broadest integration headers in Venus, depending on RPC2, util, Vice, version-vector definitions, stats, fid definitions, and Coda assertions. It is used by nearly every implementation file in this work item.

## Risks and Test Signals
Risks include namespace pollution, macro side effects, constants that must match kernel/protocol expectations, and declarations for functions without type-safe dedicated headers. Build tests across platforms and with/without `VENUSDEBUG`/`TIMING` are essential, as are protocol tests for error-code interpretation and cache-size boundary tests.
