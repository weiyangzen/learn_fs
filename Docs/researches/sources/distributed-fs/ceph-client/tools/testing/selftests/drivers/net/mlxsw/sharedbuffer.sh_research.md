<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh

Purpose: validates devlink shared-buffer occupancy reporting for physical ingress pools/TCs and CPU egress pools/TCs when IP and ARP packets traverse mlxsw.

Important functions/APIs: `h1_create`, `h2_create`, occupancy helpers `sb_occ_pool_check`, `sb_occ_itc_check`, `sb_occ_etc_check`, tests `port_pool_test`, `port_tc_ip_test`, `port_tc_arp_test`, `setup_prepare`, `cleanup`. It uses forwarding `lib.sh`, `devlink_lib.sh`, `mlxsw_lib.sh`, `devlink sb occupancy clearmax/snapshot/show`, `devlink_cell_size_get`, tc egress filters, and mausezahn.

Control flow: two ports are initialized with IPs and egress drop filters so generated packets are isolated. Each test clears max occupancy, sends one crafted packet, snapshots occupancy, then checks expected one-cell maximums in specific pools/TCs on the destination or CPU port.

State/dependencies: persistent state is tc clsact filters and devlink SB max occupancy snapshots; cleanup deletes filters and VRFs. It depends on devlink SB support, jq, accurate cell size, and deterministic CPU copy behavior. Risks include noisy background packets, stale occupancy snapshots, and hard-coded TC/pool IDs that are hardware-specific. Test signals are exact occupancy equality and per-case `log_test` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer.sh -->
