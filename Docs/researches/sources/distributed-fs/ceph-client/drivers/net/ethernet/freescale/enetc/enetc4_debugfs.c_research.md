# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc4_debugfs.c

Purpose: Provides ENETC4 debugfs visibility into MAC filtering state. It creates a per-netdev debugfs directory with a `mac_filter` file that dumps promiscuous mode bits, unicast/multicast hash filters, and optional MAC address filter table entries.

Important functions: `enetc_create_debugfs()` creates the root directory named after the netdevice and adds `mac_filter`. `enetc_remove_debugfs()` removes it. `enetc_mac_filter_show()` is the seq_file show callback. `enetc_show_si_mac_hash_filter()` reads per-SI hash filter registers. The show path queries NTMP MAFT entries through `ntmp_maft_query_entry()` when `pf->num_mfe` is nonzero.

Control flow: Opening the debugfs file invokes the generated `DEFINE_SHOW_ATTRIBUTE` path, with `struct enetc_si` in `s->private`. The show function derives PF private state via `enetc_si_priv(si)`, computes the SI count as PF plus VSIs, reads promiscuous and hash registers, then optionally walks all MAC filter table entries and prints MAC plus SI bitmap.

State and persistence: Debugfs dentries persist while the ENETC4 device is registered. It does not mutate hardware state; it reads registers and NTMP table entries. `si->debugfs_root` stores the created directory pointer for removal.

Dependencies and integration points: Depends on debugfs, seq_file, `string_choices.h`, ENETC PF private structures, ENETC4 register macros, and the NTMP MAFT query API. Built only into `nxp-enetc4.o` when `CONFIG_DEBUG_FS` is enabled.

Risks: Debugfs reads can return NTMP query errors mid-dump. The directory is created at debugfs root using the netdev name, so duplicate names or rename timing need normal debugfs handling. Register reads assume ENETC4 PF register layout and valid `pf->caps.num_vsi`/`pf->num_mfe`.

Test signals: With DEBUG_FS enabled, verify `/sys/kernel/debug/<netdev>/mac_filter` appears and disappears with device lifetime, reports SI promiscuous and hash bits accurately, handles zero `num_mfe`, and reports MAFT entries that match configured MAC filters.
