# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-2ph-1-0.c

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-csiphy-2ph-1-0.c

Purpose: Implements hardware operations for Qualcomm CAMSS two-phase CSIPHY v1.0, handling lane masks, reset, settle-count calculation, lane enable/disable, hardware-version logging, and IRQ clearing.

Important APIs/types/functions: Exports `csiphy_ops_2ph_1_0`. Key helpers are `csiphy_get_lane_mask()`, `csiphy_hw_version_read()`, `csiphy_reset()`, `csiphy_settle_cnt_calc()`, `csiphy_lanes_enable()`, `csiphy_lanes_disable()`, `csiphy_isr()`, and `csiphy_init()`.

Control flow/state: Lane mask always includes the clock lane and each configured data lane. Enabling computes settle count from link frequency and timer clock, programs init/wakeup timing, powers the selected lane mask, writes combo mode reset state, then configures every data lane plus the clock lane with CFG2, settle count, interrupt mask, and clear bits. Disabling zeros lane CFG2 registers and global power config. ISR loops over eight lane interrupt status registers, clears each, toggles global IRQ command, and clears again.

Dependencies/integration: Depends on common `camss-csiphy.h` types and higher-level CSIPHY core code for resource management, link frequency, timer clock rate, lane configuration, and ops dispatch.

Risks/test signals: If link frequency is missing, settle count becomes zero; that may work only for tolerant PHY/sensor combinations. Lane-position mistakes break CSI input before CSID sees data. Test lane masks for 1/2/4-lane sensors, link-frequency variations, interrupt storms, reset timing, and disable/re-enable cycles.
