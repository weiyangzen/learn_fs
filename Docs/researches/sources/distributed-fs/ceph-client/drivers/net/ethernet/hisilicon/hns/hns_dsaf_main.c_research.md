# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_main.c

## Purpose
`hns_dsaf_main.c` is the DSAF platform driver and hardware programming core. It parses platform configuration, maps resources, initializes DSAF fabric hardware, manages the TCAM/line MAC table software mirror, exposes DSAF stats and register dumps, controls pause/promiscuous behavior, and binds/unbinds the MAC, PPE, and AE layers.

## Important APIs and Functions
The platform entry points are `hns_dsaf_probe` and `hns_dsaf_remove`. Exported/internal service APIs include `hns_dsaf_set_mac_uc_entry`, `hns_dsaf_add_mac_mc_port`, `hns_dsaf_del_mac_entry`, `hns_dsaf_del_mac_mc_port`, `hns_dsaf_rm_mac_addr`, `hns_dsaf_clr_mac_mc_port`, `hns_dsaf_set_promisc_tcam`, `hns_dsaf_set_promisc_mode`, pause helpers, stats/string/register helpers, `hns_dsaf_fix_mac_mode`, and `hns_dsaf_wait_pkt_clean`. Hardware init is decomposed into common config, inode config, SBM config, TCAM/line init, and VOQ thresholds.

## Control Flow
Probe allocates `struct dsaf_device` plus private state, reads OF/ACPI config, initializes DSAF hardware unless in debug single-port mode, initializes MACs, initializes PPE, then registers the HNAE AE. Failure unwinds in reverse. Hardware initialization resets DSAF, programs common mode, queue IDs, STP/SW port type, interrupts, inode topology, SBM watermarks/MIB/SRAM init, TCAM/line discard defaults, and VOQ thresholds. TCAM updates are protected by `tcam_lock` and write address/data/config registers followed by pulse registers.

## State and Persistence
State is volatile. `struct dsaf_device` holds resource bases, version/mode, descriptor and buffer sizing, TCAM size, child component pointers, stats, interrupt stats, and `tcam_lock`. Private `struct dsaf_drv_priv` holds the software MAC TCAM table, where valid entries mirror hardware indexes. Hardware stats are accumulated in `hw_stats`.

## Dependencies and Integration Points
This file integrates Linux platform/OF/ACPI probing, syscon/regmap, MMIO resources, DMA mask setup, DSAF register helpers, MAC init/uninit, PPE init/uninit, RCB queue-mode helpers, misc reset operations, and HNAE AE registration. It is the foundational provider used by `hns_ae_adapt.c`.

## Risks
The TCAM software mirror and hardware can diverge if a hardware write fails because many register writes are void and not verified. Promiscuous mode reserves reverse-search TCAM entries near the end; exhaustion or failed second-stage multicast setup can leave only partial promisc state. Several waits use fixed polling limits and return `-ENODEV`/`-EBUSY` on hardware readiness failures. The config parser supports only specific mode strings in `g_dsaf_mode_match`; new firmware strings fail probe.

## Test Signals
Probe/remove on OF and ACPI systems, resource fallback ordering, invalid `desc-num`/`buf-size`/mode handling, DSAF v1/v2 init paths, TCAM add/delete for unicast/multicast/broadcast, promisc enable/disable under TCAM pressure, pause restrictions on v1, ethtool register dump count `DSAF_DUMP_REGS_NUM`, stats count v1/v2, and `hns_dsaf_wait_pkt_clean` timeout behavior should be covered.
