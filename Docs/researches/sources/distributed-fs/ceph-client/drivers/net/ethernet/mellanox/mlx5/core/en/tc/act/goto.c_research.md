# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/tc/act/goto.c

Purpose: Validates and parses TC goto-chain actions for mlx5e TC offload.

Important API: `mlx5e_tc_act_goto` provides can-offload, parse, post-parse, and marks goto as terminating. `validate_goto_chain()` checks chain range, backward-chain support, flow type, and firmware support for forwarding after reformat/decap.

Control flow: Validation chooses eswitch or NIC chain object, checks destination chain against range and direction constraints, then parse sets FWD_DEST and `attr->dest_chain`. Post-parse rejects decap+goto and mirroring goto chain rules for NIC flows.

State and dependencies: Mutates `attr->dest_chain` and action bits. Depends on eswitch chains, NIC TC chains, firmware capabilities, flow type helpers, and extack.

Risks and tests: Goto combines poorly with decap, packet reformat, mirred, and unsupported backward chains. Tests should cover FDB/NIC chain ranges, backward unsupported, FT flow rejection, decap+goto post-parse, and reformat capability gating.
