# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/Kconfig

Purpose: Defines Kconfig symbols for the RDMA Transport (RTRS) core, client, and server modules.

Important APIs/types/functions: Symbols are `INFINIBAND_RTRS` as an internal tristate core, `INFINIBAND_RTRS_CLIENT` as the user-visible "RTRS client module", and `INFINIBAND_RTRS_SERVER` as the user-visible "RTRS server module". Both client and server select the core.

Control flow: Selecting either client or server enables the shared RTRS core. The help text describes the client as a reliable RDMA transport and multipathing layer intended for a block storage initiator, and the server as the request processor for consumers such as RNBD server.

State and persistence: Build-time state only; no runtime state.

Dependencies and integration: All symbols depend on `INFINIBAND_ADDR_TRANS`, reflecting RDMA address translation requirements. The client/server options integrate with the Makefile aggregates for `rtrs-client.o`, `rtrs-server.o`, and `rtrs-core.o`.

Risks: Because the core is selected rather than user-visible, dependency drift in client/server can hide build failures. Test signals include client-only, server-only, both-enabled, and dependency-disabled kernel configs.
