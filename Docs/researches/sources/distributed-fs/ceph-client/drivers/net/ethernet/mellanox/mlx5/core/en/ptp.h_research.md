# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/ptp.h

Purpose: declares PTP channel data structures, metadata helpers, packet classification helper, and lifecycle APIs.

Important APIs/types: `struct mlx5e_ptp_metadata_fifo`, `mlx5e_ptp_metadata_map`, `mlx5e_ptpsq`, `mlx5e_ptp`, PTP state bits, `mlx5e_use_ptpsq`, FIFO/map inline helpers, open/close/activate/deactivate, RX FS helpers, `mlx5e_ptpsq_track_metadata`, and skb hwtstamp helpers.

Control flow: TX code uses `mlx5e_use_ptpsq` to route timestamped PTP skbs to PTP SQs, obtains metadata from the freelist, stores skbs in the metadata map, and later lets CQ handlers complete timestamps.

State and persistence: all structures are runtime channel state. Metadata FIFO counters are byte-sized with a mask sized to firmware metadata capacity.

Dependencies and integration: includes mlx5e core, stats, TX/RX, PTP classify/time headers, and workqueue support.

Risks: metadata FIFO/map helpers are intentionally small and assume caller-side capacity checks and synchronization. `mlx5e_use_ptpsq` relies on skb flow dissection and only selects ETH_P_1588 or UDP PTP event traffic.

Test signals: classifier coverage for L2/PTP UDP packets, metadata freelist empty checks, and compile coverage with PTP RX profile features.
