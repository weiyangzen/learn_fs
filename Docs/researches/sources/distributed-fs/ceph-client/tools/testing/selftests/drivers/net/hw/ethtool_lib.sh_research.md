# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ethtool_lib.sh

Purpose: Shared shell helpers for ethtool speed/autoneg tests.

Important APIs/functions: `speeds_arr_get()`, `ethtool_set()`, `dev_linkmodes_params_get()`, `dev_speeds_get()`, `common_speeds_get()`, and `different_speeds_get()`.

Control flow: Helpers parse ethtool supported/advertised link modes, build arrays of speed values or full mode names, identify common supported speeds between devices, and select differing speeds. `ethtool_set()` centralizes command execution and `RET` error tracking.

State and persistence: No own persistent state, but helper callers use it to mutate ethtool settings.

Dependencies and integration points: Used by ethtool hardware shell tests. Depends on ethtool text output conventions and global `RET`/`check_err` style from forwarding libs.

Risks and test signals: Parser fragility can produce false skips/failures if ethtool output changes or mode names are unexpected.
