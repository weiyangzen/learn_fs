# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Makefile

Purpose: Defines Kbuild object aggregation for RTRS core, client, server, stats, sysfs, and trace components.

Important APIs/types/functions: `rtrs-client-y` includes `rtrs-clt.o`, `rtrs-clt-stats.o`, `rtrs-clt-sysfs.o`, and `rtrs-clt-trace.o`. `rtrs-server-y` includes corresponding server objects. `rtrs-core-y` includes `rtrs.o`. Trace objects add `-I$(src)` so generated trace headers can include local files.

Control flow: Kbuild links aggregates into `rtrs-core.o`, `rtrs-client.o`, and `rtrs-server.o` according to `CONFIG_INFINIBAND_RTRS`, `CONFIG_INFINIBAND_RTRS_CLIENT`, and `CONFIG_INFINIBAND_RTRS_SERVER`.

State and persistence: Build metadata only.

Dependencies and integration: Couples the client sysfs/stats/trace helper files to the main client object and mirrors that layout for the server. The local include flag is required by Linux tracepoint generation patterns.

Risks: Omitting trace CFLAGS can break trace include generation. Missing object entries silently drop sysfs/stats/trace behavior. Test signals include modular and built-in builds, tracepoint compilation, and modpost symbol resolution.
