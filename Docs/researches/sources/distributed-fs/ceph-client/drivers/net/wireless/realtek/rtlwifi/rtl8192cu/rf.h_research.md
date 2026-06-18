
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/rf.h

Purpose: Declares CU RF6052 helper functions and RF constants.

Important APIs/functions: Defines `RF6052_MAX_TX_PWR` as `0x3F` and `RF6052_MAX_PATH` as 2. Declares bandwidth, CCK tx-power, OFDM tx-power, RF config, and RF-table replay functions. It includes both `rtl92c_*` and `rtl92cu_*` CCK/OFDM tx-power prototypes; the implemented CU functions are the `rtl92cu_*` variants used by HAL ops.

Control flow: Header only. Prototypes allow `phy.c`, `hw.c`, and `sw.c` to call RF helpers.

State and persistence: Exposed functions modify RF/BB bandwidth and tx-power registers and consume EEPROM/PHY state.

Dependencies/integration: Used by CU PHY/HW/SW and tied to RF6052 hardware. The duplicate/common-looking prototypes reflect shared 8192C naming conventions.

Risks: The `rtl92c_phy_rf6052_set_*` prototypes do not correspond to implementations in this CU file under those names, so callers should use HAL ops or the CU-named functions unless shared symbols exist elsewhere. Constant changes affect tx-power clamping and path loops.

Test signals: Build symbol resolution, HAL op invocation of CU-named functions, and tx-power clamp checks at values above `0x3F`.
