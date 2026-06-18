
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/table.c

Purpose: Provides static RTL8192CU hardware programming tables for MAC, PHY, AGC, RF path A/B, power-group offsets, and high-power board variants. These arrays are replayed by `hw.c`, `phy.c`, and `rf.c` during initialization and tx-power setup.

Important APIs/data: Defines `RTL8192CUPHY_REG_2TARRAY`, `RTL8192CUPHY_REG_1TARRAY`, `RTL8192CUPHY_REG_ARRAY_PG`, `RTL8192CURADIOA_2TARRAY`, `RTL8192CU_RADIOB_2TARRAY`, `RTL8192CU_RADIOA_1TARRAY`, `RTL8192CU_RADIOB_1TARRAY`, `RTL8192CUMAC_2T_ARRAY`, `RTL8192CUAGCTAB_2TARRAY`, `RTL8192CUAGCTAB_1TARRAY`, `RTL8192CUPHY_REG_1T_HPARRAY`, `RTL8192CUPHY_REG_ARRAY_PG_HP`, `RTL8192CURADIOA_1T_HPARRAY`, and `RTL8192CUAGCTAB_1T_HPARRAY`. Most arrays are register/value pairs; power-group arrays are register/mask/value triples.

Control flow: No executable logic. Runtime code chooses arrays based on RF type and `IS_HIGHT_PA(board_type)`, then iterates by 2 or 3 entries and writes registers with delays where needed.

State and persistence: Static read-only initialization payload in the module image. Once replayed, the values persist in hardware registers until reset or changed by later channel/power logic.

Dependencies/integration: Length constants and extern declarations live in `table.h`. `_rtl92cu_phy_param_tab_init()` installs these arrays into `rtlphy->hwparam_tables`; PHY/RF config functions consume those table slots.

Risks: Array length constants must exactly match initializer counts. Values are vendor calibration data with little local validation. High-power variants differ in PHY, PG, RadioA, and AGC tables; wrong board detection can over/underdrive RF. `RTL8192CU_RADIOB_1TARRAY` is a one-entry zero table, so path B must not be meaningfully configured for 1T hardware.

Test signals: Build-time array bounds, init register trace comparison against vendor tables, 1T/2T/high-PA hardware bring-up, RF calibration success, receive sensitivity and transmit EVM checks after table replay.
