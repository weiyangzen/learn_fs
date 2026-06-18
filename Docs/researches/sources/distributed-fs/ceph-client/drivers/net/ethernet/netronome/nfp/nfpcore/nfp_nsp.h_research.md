# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp_nsp.h

Purpose: Declares the NSP command API, ABI feature predicates, Ethernet port/config structures, firmware policy constants, identify/sensor interfaces, media buffers, and version parsing helpers.

Important APIs/types/functions: `nfp_nsp_*()` covers lifecycle and commands. Inline `nfp_nsp_has_*()` predicates encode ABI minor thresholds. `enum nfp_eth_interface/media/aneg/fec`, FEC bit masks, `struct nfp_eth_table` and nested port structure define the Ethernet table contract. Config helpers include `nfp_eth_config_start()`, commit/cleanup, and `__nfp_eth_set_*()`.

Control flow/state: Header documents staged Ethernet configuration: callers open config state, mutate entries through helper setters, then commit or cleanup. NSP handles also carry ABI version used by feature predicates.

Dependencies/integration: Used by `nfp_nsp.c`, `nfp_nsp_eth.c`, `nfp_nsp_cmds.c`, NIC probe, ethtool, hwmon, and firmware management code.

Risks: ABI thresholds must match management firmware behavior. Ethernet table fields mix raw firmware state and computed driver state; callers must not assume all fields are valid on older ABI versions.

Test signals: Compile all NSP consumers, run ABI-minor feature matrix tests, verify port table parsing, config commit/cleanup behavior, and version/media/sensor query paths.
