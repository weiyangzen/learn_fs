# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.c

Purpose: handles per-packet IPsec TX/RX data path transformations around mlx5e WQE construction and CQE receive completion.

Important APIs/types/functions: `mlx5e_ipsec_set_iv_esn`, `mlx5e_ipsec_set_iv`, `mlx5e_ipsec_handle_tx_wqe`, `mlx5e_ipsec_tx_build_eseg`, `mlx5e_ipsec_handle_tx_skb`, `mlx5e_ipsec_offload_handle_rx_skb`, and `mlx5_esw_ipsec_rx_make_metadata`. Local helpers remove ESP trailer, set SWP offsets, and calculate TX inline trailer state.

Control flow and state: TX validates single-SA secpath, offload handle, and IP/IPv6 protocol; non-GSO packets have software trailer removed before hardware insertion; IV bytes are written from XFRM sequence, with ESN handling for GSO mid-scope wrap; state records trailer length and protocol; ESEG gets IPsec metadata, trailer insertion flags, SWP parser offsets, and checksum associations. RX reads metadata handle, allocates secpath, looks up SA in SADB under RCU, holds the XFRM state, appends it to secpath, and marks `xfrm_offload` as crypto done/success.

Dependencies and integration: depends on XFRM secpath/offload state, Linux ESP helpers, mlx5 ESEG fields, IPsec SADB from `ipsec.h`, eswitch IPsec object ID mapping, and stats counters.

Risks and test signals: bad trailer trimming corrupts SKBs; secpath allocation or SADB miss must not leave invalid XFRM references; SWP offsets vary by tunnel/transport/encap. Test TX drop counters for bundles/no-state/not-IP/trailer errors, GSO ESN wrap, checksum offload paths, RX SADB miss, secpath allocation failure, and switchdev metadata lookup.
