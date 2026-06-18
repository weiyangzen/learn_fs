# sources/distributed-fs/openafs/src/xstat/xstat_cm.c

## Purpose

`xstat_cm.c` implements the client side of Cache Manager extended statistics collection. It creates unauthenticated Rx connections to one or more cache managers, starts a pthread probe loop, periodically calls `RXAFSCB_GetXStats` for requested collection ids, stores the latest result in exported globals, and invokes a caller-provided handler after each collection.

## Important APIs, Types, and Variables

- Exported globals: `xstat_cm_numServers`, `xstat_cm_ConnInfo`, `xstat_cm_Results`, and `xstat_cmData`.
- Private state: probe frequency, initialization flag, debug flag, one-shot flag, handler pointer, probe thread id, collection count/id array, and a mutex/condition variable for forced probes.
- `xstat_cm_CleanupInit` resets result pointers and fixed result buffer metadata.
- `xstat_cm_Cleanup` destroys Rx connections and optionally frees the connection array.
- `xstat_cm_Init` validates arguments, records configuration, allocates/copies collection ids, initializes Rx/security, creates per-server Rx connections, and starts the probe thread.
- `xstat_cm_LWP` is the probe thread body; it iterates servers and collection ids, calls `RXAFSCB_GetXStats`, fills `xstat_cm_Results`, and invokes the handler.
- `xstat_cm_ForceProbeNow` signals the condition variable so a continuous probe wakes early.
- `xstat_cm_Wait` joins one-shot probes or sleeps/selects in continuous mode.

## Control Flow

Initialization is mandatory before all other operations. `xstat_cm_Init` rejects invalid server counts, socket arrays, probe intervals, handlers, collection counts, and collection arrays. It sets global mode flags, allocates storage, initializes result state, calls `rx_Init`, creates a null security object, resolves host names for display, creates service-1 Rx connections to each target cache manager, and starts `xstat_cm_LWP`.

The probe thread increments `probeNum` once per round. For each valid connection and each requested collection id, it resets the static data buffer length/content, records the target connection and collection number, calls `RXAFSCB_GetXStats`, stores the RPC result code in `probeOK`, and calls the handler with no explicit arguments; the handler reads exported globals. In one-shot mode the thread exits after one full pass. In continuous mode it waits on `xstat_cm_force_cv` until the next absolute timeout or a forced signal.

Cleanup destroys any existing Rx connections and can free the connection array, but it does not join or cancel the probe thread in continuous mode.

## State and Persistence Behavior

All state is process-local memory. The latest probe result uses a fixed global `xstat_cmData` buffer of `AFSCB_MAX_XSTAT_LONGS`, so each collection overwrites previous data. There is no local persistence. Network state consists of Rx connections to cache managers. The module is effectively singleton: repeated `xstat_cm_Init` calls are accepted as no-ops after printing a warning.

## Dependencies and Integration Points

The file depends on Rx, the generated AFS callback interface (`RXAFSCB_GetXStats`), pthreads, opr mutex/condition wrappers, host utility resolution, and `xstat_cm.h`. Consumers are typically `xstat_cm_test` or monitoring tools that install a handler and inspect `xstat_cm_Results`.

## Risks and Edge Cases

- Global result state is not protected while the handler and probe thread operate; consumers must treat it as thread-owned during callbacks.
- `malloc` for `xstat_cm_collIDP` is not checked before `memcpy`.
- Continuous cleanup does not stop/join the probe thread, so freeing memory while it runs would be unsafe.
- A connection creation failure sets a final `-2` return but still starts the probe thread and leaves null connections skipped.
- `xstat_cm_Results.data.AFSCB_CollData_len` is reset to max before each call, and the buffer is memset using `AFSCB_MAX_XSTAT_LONGS * 4`, assuming 32-bit `afs_int32`.
- Null Rx security is intentional for this probe interface but should be considered when exposing stats across trust boundaries.

## Test Signals

Tests should cover invalid argument rejection, one-shot completion and `pthread_join`, forced wakeups in continuous mode, handler invocation count for N servers times M collections, null connection skipping after partial init failure, Rx init/security failure injection, cleanup destroying connections, and correct result metadata (`probeNum`, `probeTime`, `connP`, `collectionNumber`, `probeOK`, data length).
