# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_dcb.c

## Purpose

`hclge_dcb.c` implements PF Data Center Bridging support for the HNS3 driver. It bridges Linux DCBNL IEEE ETS/PFC/app callbacks and `tc mqprio` offload into the driver's traffic-manager state (`hdev->tm_info`) and hardware programming. The file is compiled when `CONFIG_HNS3_DCB` is enabled and installs `hnae3_dcb_ops` for PF vport 0 only.

## Important APIs And Functions

The exported entry point is `hclge_dcb_ops_set()`, which checks `hnae3_dev_dcb_supported(hdev)` and PF vport identity, then sets `vport->nic.kinfo.dcb_ops` and initializes `hdev->dcbx_cap` to IEEE host-managed DCBX.

DCBNL callbacks include `hclge_ieee_getets()`, `hclge_ieee_setets()`, `hclge_ieee_getpfc()`, `hclge_ieee_setpfc()`, `hclge_ieee_setapp()`, `hclge_ieee_delapp()`, `hclge_getdcbx()`, and `hclge_setdcbx()`. `hclge_setup_tc()` implements hardware-offloaded `mqprio` channel mode. Helper functions translate between `struct ieee_ets` and TM state, validate TC counts and priority maps, recalculate PFC maps, synchronize mqprio options into `struct hnae3_tc_info`, and reconfigure hardware with `hclge_map_update()`.

## Control Flow

ETS set flow validates DCBX mode and rejects changes while mqprio is active. `hclge_ets_validate()` derives TC count from `prio_tc`, ensures it is within `tc_max` and allocated TQPs, validates SP versus ETS scheduling, rejects ETS bandwidth on disabled TCs, requires nonzero ETS weights, and enforces total ETS bandwidth of 100 percent when any ETS TC exists. If the priority-to-TC map or TC count changes, the driver notifies the NIC client down and uninit, updates TM scheduling information, applies ETS to TM fields, reprograms TM, pause, buffer allocation, RSS indirection, and RSS hardware, then notifies init and up. If only DWRR weights change, it programs `hclge_tm_dwrr_cfg()`.

PFC set flow computes hardware PFC TC bitmap from user priorities and current priority-to-TC mapping, updates `tm_info.hw_pfc_map` and `tm_info.pfc_en`, refreshes TM PFC state, reprograms pause, brings the client down, flushes TM, reallocates buffers, unflushes TM, and brings the client up. DSCP app set/delete maintains `h->kinfo.dscp_prio[]`, calls kernel `dcb_ieee_setapp()` or `dcb_ieee_delapp()`, updates DSCP-to-TC mapping in hardware, and switches `tc_map_mode` between DSCP and priority mapping.

`hclge_setup_tc()` rejects changes before NIC registration and while DCB ETS is active. It validates queue counts as powers of two, enforces continuous offsets from zero, rejects unsupported min/max rate settings, applies down/uninit notifications, updates `kinfo->tc_info`, reprograms TC hardware, and rolls back on failures except for mqprio destroy, which is warned as recoverable after reset.

## State And Persistence Behavior

The file mutates `hdev->tm_info`, `hdev->dcbx_cap`, `vport->nic.kinfo.tc_info`, `vport->nic.kinfo.tc_map_mode`, `h->kinfo.dscp_prio[]`, and `h->kinfo.dscp_app_cnt`. Hardware persistence is through TM scheduler, pause, buffer, RSS, DSCP map, and priority map commands. Client notification ordering protects queue/ring state by taking networking down before major TC map changes and bringing it up afterward.

## Dependencies And Integration Points

It depends on `hclge_main.h`, `hclge_tm.h`, `hclge_dcb.h`, DCBNL IEEE types, Linux `dcb_ieee_*` helpers, and HNS3 client notification callbacks. Probe calls `hclge_dcb_ops_set()` from `hclge_main.c`. DCB operations interact with RSS, pause configuration, TM flush, buffer allocation, MAC stats, PFC stats, and netdev debug logging.

## Risks

Risk concentrates around partial reconfiguration. Several flows update software state before all hardware steps succeed, so rollback coverage matters. PFC set returns the last bad error after attempting cleanup, but `tm_info.pfc_en` remains updated even if later hardware operations fail. ETS map changes rely on down/uninit and init/up notifications; missed notification errors can leave client and hardware state out of sync. DSCP app operations must roll back both kernel DCB app tables and driver arrays when hardware mapping fails. mqprio destroy has an explicit nonfatal failure path where reset is expected to restore state.

## Test Signals

Exercise `dcb` or `lldptool` IEEE ETS/PFC get and set, invalid bandwidth totals, invalid priority-to-TC maps, mqprio activation and destruction, DSCP app add/delete, PFC statistics reads, and reset after DCB changes. Watch for netdev down/up notification errors, traffic continuity across TC reconfiguration, RSS queue distribution after TC count changes, and buffer allocation failures.
