# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/hal_btcoex.h

Purpose: this header declares the HAL Bluetooth coexistence interface used by RTL8723B Wi-Fi code to coordinate shared antenna/RF/power behavior with Bluetooth.

Important APIs/types/macros: `struct bt_coexist` stores whether BT exists, antenna count, BT chip type, and initialization status. Notifications include `hal_btcoex_IpsNotify`, `LpsNotify`, `ScanNotify`, `ConnectNotify`, `MediaStatusNotify`, `SpecialPacketNotify`, `IQKNotify`, `BtInfoNotify`, `SuspendNotify`, and `HaltNotify`. Configuration/control APIs include `hal_btcoex_SetBTCoexist`, `SetPgAntNum`, `SetSingleAntPath`, `Initialize`, `PowerOnSetting`, `InitHwConfig`, `Handler`, `GetRaMask`, and power-mode helpers.

Control flow and integration: HAL init calls power-on and hardware-config functions; EFUSE parsing configures coexistence, antenna count, and single-antenna path; scan/join/IQK paths send notifications; C2H BT info events are forwarded from receive/interrupt handling; rate-mask updates subtract the BT coexistence RA mask.

State and persistence: runtime state lives in `hal_com_data.bt_coexist` plus additional implementation-private coexistence state outside this header. Parsed EFUSE values in `hal_com_data` drive initial BT coexistence configuration.

Dependencies: includes `drv_types.h`, which creates a heavy include cycle but gives all prototypes access to `struct adapter`.

Risks and test signals: coexistence callbacks are invoked from init, MLME transitions, C2H event paths, and calibration, so ordering and context matter. Missing or incorrect BT EFUSE parsing can select the wrong antenna path. Tests should cover BT-present and BT-absent boards, single/two antenna settings, scan/connect notifications, IQK notification pairing, C2H BT info handling, and rate-mask adjustment under BT activity.
