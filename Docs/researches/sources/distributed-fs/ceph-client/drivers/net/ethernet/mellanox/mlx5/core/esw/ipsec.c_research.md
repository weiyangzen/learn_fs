# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/ipsec.c

Purpose: Manages VF IPsec offload capabilities through eswitch-managed HCA capability queries and updates on other functions.

Important APIs/types/functions: Public functions query and set VF crypto and packet/full IPsec offload support: `mlx5_esw_ipsec_vf_offload_get()`, `mlx5_esw_ipsec_vf_offload_supported()`, `mlx5_esw_ipsec_vf_crypto_offload_supported()`, `mlx5_esw_ipsec_vf_packet_offload_supported()`, `mlx5_esw_ipsec_vf_crypto_offload_set()`, and packet set. Internal helpers get/set generic `ipsec_offload`, set typed IPsec caps, and set crypto auxiliary Ethernet offload `insert_trailer`.

Control flow: Capability get first verifies generic VF IPsec offload is meaningful and enabled, then reads IPsec caps into `vport->info.ipsec_crypto_enabled` and `ipsec_packet_enabled`. Set-by-type rejects PF vport, optionally sets crypto auxiliary caps, enables generic IPsec before typed caps when turning on, and when turning off clears typed cap, refreshes current state, and disables generic IPsec only if both typed capabilities are now off.

State and persistence: Persistent state is firmware HCA capability state for the target vport/function and cached booleans in `vport->info`. Query/set buffers are temporary kernel allocations.

Dependencies and integration: Depends on VHCA resource manager support, other-function capability query/set commands, firmware feature detection via `reformat_add_esp_trasport`, IPsec cap groups, Ethernet offload caps, flow table decap support, and eswitch devlink port function IPsec knobs.

Risks and test signals: Risks include enabling typed caps without generic cap, failing to disable generic cap only when safe, stale cached state on set failure, and firmware generations that misreport IPsec support. Test signals include devlink port function IPsec crypto/packet get/set on VFs, unsupported PF attempts, old firmware capability rejection, and both crypto plus packet toggled independently.
