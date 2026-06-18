# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_cna.h

Purpose: CNA/CEE data definition header for port statistics and Converged Enhanced Ethernet query results.

Important APIs/types/functions: defines `struct bfa_port_fc_stats`, `struct bfa_port_eth_stats`, `union bfa_port_stats_u`, LLDP/DCBX constants, `struct bfa_cee_lldp_str`, `struct bfa_cee_lldp_cfg`, `enum bfa_cee_dcbx_version`, `enum bfa_cee_lls`, `struct bfa_cee_dcbx_cfg`, `enum bfa_cee_status`, `struct bfa_cee_attr`, and `struct bfa_cee_stats`.

Control flow: no executable flow. Firmware fills these packed structures into DMA memory; `bfa_cee.c` copies and converts selected fields before returning data to callers. Port statistics can be consumed by adapter statistics paths.

State and persistence behavior: all structures represent runtime counters or negotiated remote LLDP/DCBX/CEE state. Counters are cumulative until reset by firmware. The LLDP/DCBX attributes reflect remote peer-advertised state and current link CEE status.

Dependencies and integration points: includes `bfa_defs.h` for common BFA types and status dependencies. Integrated by the CEE mailbox client and any ethtool/debugfs/statistics presentation code.

Risks: `__packed` data is firmware ABI; misalignment-sensitive CPU access or missing byte-order conversion can produce wrong values. Stats are 32-bit in `bfa_cee_stats`, so wraparound is possible on active links. Fixed LLDP string buffers require consumers to honor `len` and avoid assuming NUL termination.

Test signals: LLDP/DCBX dumps should show sane remote chassis/port/system strings, TTL, PFC and priority maps. Statistics should increment under LLDP/DCBX activity and reset through firmware paths where available.
