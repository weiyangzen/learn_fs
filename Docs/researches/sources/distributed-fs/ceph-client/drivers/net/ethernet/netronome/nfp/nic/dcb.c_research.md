# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/dcb.c

Purpose: Implements DCBNL IEEE 802.1Qaz support for the NFP NIC app by mapping user DCB settings into a firmware runtime symbol table and notifying firmware through the netdev mailbox.

Important APIs/types/functions: `struct nfp_dcb` is defined in `main.h`; this file operates on it via `get_dcb_priv()`. DCBNL ops include ETS get/set, maxrate get/set, DSCP app set/delete. Helpers write PCP/DSCP-to-TC indexes, TSA, bandwidth percentage, max rates, enable/trust fields, and mailbox update masks. `nfp_nic_dcb_init()` maps `net.dcbcfg_tbl`; `nfp_nic_dcb_clean()` releases it.

Control flow: Init maps the firmware DCB config table runtime symbol for each vNIC and initializes default TC/prio/rate/TSA state before attaching `dcbnl_ops`. Set ETS validates bandwidth rules, updates cached arrays, refreshes strict-priority TC index mapping, writes firmware table fields, ensures rate/trust/enable state, then sends `NFP_NET_CFG_MBOX_CMD_DCB_UPDATE`. Maxrate and DSCP app paths similarly update the mapped table and notify firmware.

State and persistence: Driver keeps per-vNIC DCB arrays and flags in `app_priv`. Firmware-visible state is written into mapped CPP memory and committed through mailbox commands. DSCP app entries are also tracked by the kernel DCB app list.

Dependencies/integration: Depends on `CONFIG_DCB`, net/dcbnl, NFP app/net structures, runtime symbol mapping via `nfp_pf_map_rtsym()`, CPP area cleanup, and NFP net mailbox APIs.

Risks: Mapped table offsets are ABI-sensitive (`NFP_DCB_CFG_STRIDE`, field offsets, update masks). Trust mode changes depend on DSCP count. Maxrate conversion uses kbps-to-mbps and reserves `0xffff` for unlimited. Mailbox lock/reconfig failures must avoid diverging cached state from firmware.

Test signals: DCB init with present/missing `net.dcbcfg_tbl`, ETS validation failure for bad bandwidth sums, maxrate boundary `>=0xffff` Mbps, DSCP set/delete and trust fallback, mailbox failure propagation, and cleanup releasing the mapped CPP area.
