# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/int_port.h

Purpose: Declares internal-port offload types and APIs, with stubs for builds without `CONFIG_MLX5_CLS_ACT`.

Important types and APIs: `enum mlx5e_tc_int_port_type` distinguishes ingress and egress internal ports. APIs cover support check, init/cleanup, representor RX lifecycle, skb forwarding, get/put, metadata accessors, and flow-source selection.

Control flow and state: Callers obtain a refcounted `mlx5e_tc_int_port` and later put it; metadata and flow source are used when building match/action rules.

Dependencies and integration: Includes `en.h`; consumed by TC action parsers and offload restore paths.

Risks and tests: Stub coverage is incomplete for some functions when `CONFIG_MLX5_CLS_ACT` is disabled; compile configurations should be tested. Runtime tests should cover ingress vs egress flow source and metadata matching.
