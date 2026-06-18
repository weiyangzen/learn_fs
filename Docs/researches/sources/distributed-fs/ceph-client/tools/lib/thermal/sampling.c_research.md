# sources/distributed-fs/ceph-client/tools/lib/thermal/sampling.c

Purpose: Subscribes to thermal sampling netlink group and dispatches temperature sample messages to the user `tz_temp` callback.

Important APIs/types/functions: Public APIs are `thermal_sampling_init()`, `thermal_sampling_exit()`, `thermal_sampling_handle()`, and `thermal_sampling_fd()`. Internal `handle_thermal_sample()` decodes sampling messages.

Control flow: Init connects a netlink socket and subscribes to `THERMAL_GENL_SAMPLING_GROUP_NAME`. Handle sets a valid callback and receives messages. The handler switches on `genlhdr->cmd`; for `THERMAL_GENL_SAMPLING_TEMP`, it extracts thermal zone id and temperature and invokes `th->ops->sampling.tz_temp()`.

State and persistence: Mutates sampling socket/callback fields on `struct thermal_handler`. Runtime-only event processing.

Dependencies/integration: Depends on public `thermal.h`, private `thermal_nl.h`, libnl, and Linux thermal sampling UAPI constants.

Risks: No NULL check for `th->ops` or `th->ops->sampling.tz_temp`; enabling sampling without callback can crash. Missing message attributes can crash. Exit returns before disconnect if unsubscribe fails. Init does not clean up the socket if subscription fails.

Test signals: Simulate sample event, unknown command, NULL handler, NULL callback, missing attrs, subscription failure, and fd retrieval.
