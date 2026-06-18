# sources/distributed-fs/ceph-client/net/mctp/Makefile

Purpose: builds the MCTP core object and optional test utility object.

Important entries: `obj-$(CONFIG_MCTP) += mctp.o`; `mctp-objs := af_mctp.o device.o route.o neigh.o`; `obj-$(CONFIG_MCTP_TEST) += test/utils.o`.

Control flow and state: links socket, device, route, and neighbour implementation into one MCTP object. Route and socket test sources are included from their production C files when configured, while shared test utilities are separate.

Dependencies and integration: driven by Kconfig. Build correctness depends on include-style KUnit tests resolving static symbols in `af_mctp.c` and `route.c`.

Risks and test signals: changing object composition can break static test access. Build with `CONFIG_MCTP`, `CONFIG_MCTP_TEST`, and module/built-in variants where allowed.
