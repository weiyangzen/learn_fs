# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/htb.c

Purpose: implements the mlx5e software HTB offload tree and maps Linux `tc_htb_qopt_offload` operations to mlx5 firmware QoS nodes plus per-leaf transmit queues.

Important APIs/functions: `mlx5e_htb_init`, `mlx5e_htb_cleanup`, `mlx5e_htb_enumerate_leaves`, `mlx5e_htb_get_txq_by_classid`, `mlx5e_htb_leaf_alloc_queue`, `mlx5e_htb_leaf_to_inner`, `mlx5e_htb_leaf_del`, `mlx5e_htb_leaf_del_last`, and `mlx5e_htb_node_modify`. Internal state is `struct mlx5e_htb` and `struct mlx5e_qos_node`, using a classid hash table plus a leaf-qid bitmap.

Control flow: HTB creation prepares the select-queue state, allocates QoS SQ storage when the netdev is open, creates a root software node, creates the firmware root, and applies the select-queue change. Leaf creation allocates a compact qid, creates a software leaf, converts byte rates to firmware bandwidth share/max-average-bw, creates a firmware leaf, and opens/activates a QoS SQ if channels are up. Leaf-to-inner and leaf-delete-last are two-step firmware topology transitions that reuse qids while stopping queues and resetting qdiscs to prevent traffic leakage between classes. Deletion compacts qids by moving the highest active QoS SQ into the removed qid slot.

State and persistence: state is in memory only. Node lookup is RCU-visible to the TX datapath, and qid changes use `WRITE_ONCE`, `synchronize_net`, and qdisc resets. Firmware object ids are kept in nodes and destroyed best-effort on teardown or topology mutation.

Dependencies and integration: depends on `en/htb.h`, `en.h`, mlx5 core QoS firmware helpers, `qos.c` SQ lifecycle helpers, and `selq` queue selection. It is driven by `mlx5e_htb_setup_tc` in `qos.c`.

Risks: firmware failures during topology conversion can leave partial hardware state that is handled with rollback or force-mode cleanup. Queue compaction is subtle because qid exposure, netdev queue counts, qdisc state, and SQ lifecycle must remain synchronized. Rate conversion treats firmware `0` bandwidth share as unlimited, so low/invalid rates rely on upstream validation.

Test signals: exercise HTB create/destroy, leaf add/delete/modify, leaf-to-inner promotion, last-child collapse, open vs closed netdev paths, firmware error injection, qid compaction, and concurrent TX queue selection during class deletion.
