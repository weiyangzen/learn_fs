# sources/distributed-fs/ceph/src/mds/MDSDaemon.h

## Purpose

`MDSDaemon.h` declares the top-level MDS daemon dispatcher and process-lifecycle object. It exposes daemon initialization, signal handling, clean-shutdown inspection, the global MDS lock, and protected/private hooks for admin socket, tick, message dispatch, authentication, shutdown, and respawn.

## Important APIs And State

Public methods are `MDSDaemon`, destructor, `get_starttime`, `get_uptime`, `handle_signal`, `init`, and `is_clean_shutdown`. The public `mds_lock` and `stopping` flag are central: comments require every lock holder to check `stopping` and either do no work or never drop the lock again.

Protected methods include `reset_tick`, `wait_for_omap_osds`, `set_up_admin_socket`, `clean_up_admin_socket`, `check_ops_in_flight`, `asok_command`, `dump_status`, `suicide`, `respawn`, `tick`, `handle_core_message`, `handle_command`, and `handle_mds_map`. Private messenger overrides are `ms_dispatch2`, auth/connect/reset handlers, and `parse_caps`.

State includes `Beacon`, daemon `name`, `Messenger*`, `MonClient*`, `io_context`, `MgrClient`, current `MDSMap`, `LogClient`, cluster log channel, optional `MDSRankDispatcher`, timer tick event, admin socket hook, original argv for respawn, and start time.

## State And Persistence Behavior

This header models runtime process state, not filesystem persistence. Persistent effects are indirect: map transitions create/drive rank dispatchers; shutdown state updates beacons and monitor-visible wanted state; authentication parsing determines session capabilities. `orig_argc`/`orig_argv` preserve command-line state for process replacement.

## Dependencies And Integration Points

It inherits from `Dispatcher`, depends on `Beacon`, `LogClient`, `Timer`, `MgrClient`, `Messenger`, `MonClient`, `MDSMap`, `MCommand`, `MMDSMap`, and `MDSAuthCaps`. `MDSRankDispatcher` owns rank-specific metadata subsystems after rank assignment.

## Risks And Test Signals

The API makes `mds_lock` public because many subsystems coordinate through it, so lock discipline is the main risk. Tests should verify dispatcher behavior while rankless, while stopping, and after DNE desired state. Clean shutdown should distinguish rankless standby from active rank stop. `parse_caps` should reject undecodable buffers and malformed strings consistently with fast authentication and accept handling.
