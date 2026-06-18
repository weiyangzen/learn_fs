# sources/distributed-fs/ceph-client/tools/lib/thermal/thermal_nl.c

Purpose: Implements low-level libnl helpers for connecting to generic netlink, sending messages synchronously, resolving thermal multicast group IDs, and subscribing/unsubscribing.

Important APIs/types/functions: Public-private APIs include `nl_send_msg()`, `nl_thermal_connect()`, `nl_thermal_disconnect()`, `nl_subscribe_thermal()`, and `nl_unsubscribe_thermal()`. Internal callbacks handle sequence checks, netlink errors, finish, ack, and family multicast group parsing.

Control flow: `nl_thermal_connect()` allocates callbacks and socket, connects generic netlink, and installs error/finish/ack/seq callbacks. `nl_send_msg()` sends a message, installs the caller rx handler, then loops receiving until `done` or `err`. Multicast resolution sends `CTRL_CMD_GETFAMILY` for the thermal family, parses nested multicast groups, and returns the requested group id. Subscribe/unsubscribe add/drop socket membership.

State and persistence: Uses thread-local `err` and `done` flags shared by callbacks in the current thread. Socket/callback objects are allocated and returned to callers. No file persistence.

Dependencies/integration: Depends on libnl core/genl/ctrl APIs and thermal UAPI names from `thermal.h`/`thermal_nl.h`.

Risks: `nl_thermal_connect()` returns `THERMAL_ERROR` without freeing socket/callback if callback setup fails. `nl_send_msg()` can spin indefinitely if callbacks never set `done` or `err`. Thread-local flags help per-thread concurrency but one thread using multiple sockets concurrently still shares flags. `nl_get_multicast_id()` does not check `genlmsg_put()`/`nla_put_string()` failures before send.

Test signals: Mock libnl for connect failures at each step, callback setup failure, send error, ack/finish/error callbacks, group resolution success/missing group, subscribe/unsubscribe failure, and concurrent sends.
