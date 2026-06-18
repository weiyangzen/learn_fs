
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.h

Purpose: Declares CU dynamic-management interfaces while importing the CE dynamic-management definitions that hold shared thresholds, enums, and helper prototypes.

Important APIs/types/functions: Includes `../rtl8192ce/dm.h`, then declares `rtl92cu_dm_dynamic_txpower()`, `dm_savepowerindex()`, `dm_writepowerindex()`, and `dm_restorepowerindex()`. The `dm_*powerindex` helpers are implemented in shared code but used by CU dynamic tx-power transitions.

Control flow: Header only. Its declarations let `hw.c`, `sw.c`, and `dm.c` wire the dynamic tx-power callback into `rtl_hal_ops`.

State and persistence: No direct state. It exposes functions that operate on `rtlpriv->dm` and PHY power index registers.

Dependencies/integration: Bridges CU files to CE/common dynamic-management support. Because CU borrows CE DM declarations, changes in the CE header affect CU compile and behavior.

Risks: Prototype drift between this header and shared implementations would be caught at compile time. Semantic drift in CE DM constants can alter CU tx-power behavior without changing this file.

Test signals: Build should verify prototypes. Runtime watchdog testing should confirm `.dm_dynamic_txpower` invokes the CU implementation and shared power-index save/write/restore functions resolve correctly.
