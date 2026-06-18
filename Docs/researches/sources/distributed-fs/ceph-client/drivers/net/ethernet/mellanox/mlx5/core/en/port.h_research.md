# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/port.h

Purpose: declares Ethernet port register helper APIs and mlx5e FEC policy constants.

Important APIs/functions: autoneg query/set, link speed query, PBMC/SBPR/SBCM/PPTB buffer helpers, FEC capability/get/set helpers, and enum values for NOFEC, Firecode, RS variants, and LLRS.

Control flow: higher-level ethtool/DCB/port-buffer code calls these wrappers rather than building raw mlx5 register commands directly.

State and persistence: header has no state. Register writes performed by the implementation change firmware/admin state.

Dependencies and integration: includes mlx5 core driver types and `en.h`; used heavily by `port_buffer.c` and ethtool link settings paths.

Risks: enum values must stay aligned with firmware/ethtool translation code. Callers must pass adequately sized register buffers for query functions that accept `void *out`.

Test signals: compile coverage plus link mode, buffer, and FEC ethtool tests.
