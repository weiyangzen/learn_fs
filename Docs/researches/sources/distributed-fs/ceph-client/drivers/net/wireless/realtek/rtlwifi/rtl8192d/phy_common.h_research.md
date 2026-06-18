# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/phy_common.h

Purpose: Declares shared RTL8192D PHY/RF constants, enums, lock helpers, and calibration/TX-power/MACPHY functions.

Important APIs/types: Defines target channel counts, IQK constants, baseband and RF content enums, CCK/page-A lock helpers for dual-interface PCI, RF query/set, BB/RF register-definition initialization, TX-power setup, RF environment save/restore, calibration register save/restore, curve-index calculation, IQK reset, IO command handling, MAC/PHY mode setup, channel grouping, coexistence RF-page setup, and PCI RF lock helpers.

Control flow: Inline helpers conditionally lock only for PCI dual-interface cases and no-op for USB. The exported declarations describe setup flow from hardware initialization through calibration and channel/power updates.

State and persistence: No header-owned state. Helpers operate on `rtl_priv` locks and `rtl_phy`/`rtl_hal` state.

Dependencies and integration: Requires rtlwifi type definitions, `enum radio_path`, `enum io_type`, and interface constants. Included by shared DM/RF/HW and rtl8192de PHY/HW code.

Risks: The same function names appear as `static inline` definitions plus external declarations to satisfy sparse, which is unusual but intentional. Lock helper behavior depends on `rtlhal.interface` and `interfaceindex`; wrong initialization can skip required protection.

Test signals: Compile and sparse context-balance checks, plus runtime RF access on PCI and USB builds if both are present.
