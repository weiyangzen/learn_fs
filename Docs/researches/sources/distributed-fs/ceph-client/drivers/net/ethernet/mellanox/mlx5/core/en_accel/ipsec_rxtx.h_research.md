# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_accel/ipsec_rxtx.h

Purpose: declares IPsec packet data path helpers and metadata interpretation macros for mlx5e TX/RX.

Important APIs/types/functions: metadata macros extract marker, syndrome, and handle from CQE FT metadata; `struct mlx5e_accel_tx_ipsec_state` stores active TX XFRM offload, state, trailer length, and padding length. Declares TX/RX handlers, IV setters, ESW metadata lookup, ESEG build, feature check, checksum ESEG helper, and disabled stubs.

Control flow and state: inline feature check disables checksum/GSO for software IPsec or unsupported L4 protocols. `mlx5e_ipsec_txwqe_build_eseg_csum` only acts when ESEG IPsec metadata is present, then configures outer/inner checksum flags from XFRM offload protocol fields.

Dependencies and integration: includes XFRM, SKB, mlx5e TX/RX structures, and is included by `en_accel.h` and RX completion code.

Risks and test signals: metadata bit layout must match flow steering; feature fallback must prevent software IPsec checksum/GSO misuse. Build with/without IPsec and test feature negotiation, checksum flags for transport/tunnel, and metadata handle decode.
