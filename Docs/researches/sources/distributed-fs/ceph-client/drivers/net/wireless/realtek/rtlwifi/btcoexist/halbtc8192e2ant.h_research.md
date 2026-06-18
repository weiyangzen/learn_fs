# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8192e2ant.h

## Purpose
Defines the RTL8192E two-antenna Bluetooth coexistence contract shared by the chip-specific implementation and the rtlwifi coexistence dispatcher. It names BT-info bit fields, BT-info report sources, BT status states, coexistence algorithm IDs, the two main state structures, and the external notification/display entry points implemented by the companion C file.

## Important APIs, Types, And Functions
The BT-info byte bits identify FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection state. `BTC_RSSI_COEX_THRESH_TOL_8192E_2ANT` provides the hysteresis tolerance used by RSSI state helpers.

`enum bt_info_src_8192e_2ant` identifies reports from Wi-Fi firmware, BT response, and BT active/auto report. `enum bt_8192e_2ant_bt_status` normalizes parsed BT info into non-connected idle, connected idle, inquiry/page, ACL busy, SCO busy, ACL+SCO busy, or max/undefined. `enum bt_8192e_2ant_coex_algo` enumerates the policy branches used by `btc8192e2ant_run_coexist_mechanism()`: SCO, SCO+PAN, HID, A2DP, A2DP+PAN-HS, PAN-EDR, PAN-HS, PAN+A2DP, PAN+HID, HID+A2DP+PAN, and HID+A2DP.

`struct coex_dm_8192e_2ant` is the dynamic mechanism state cache and contains previous/current firmware, software, and hardware coexistence settings plus backups and selected algorithm. `struct coex_sta_8192e_2ant` records observed station/environment state such as BT profile presence, IPS/LPS, counters, RSSI, C2H info, inquiry/page, retry count, and BT-info extensions. The exported `ex_btc8192e2ant_*` prototypes are the integration points for init, power-save notifications, scan/connect/media/special-packet events, BT-info delivery, stack-operation notification, halt, periodic maintenance, and seq-file display.

## Control Flow
The header itself has no control flow, but its declarations mirror the runtime contract. The common coexistence layer calls the `ex_btc8192e2ant_*` functions on lifecycle and wireless events. The implementation uses the enums to convert raw C2H bytes into normalized BT status and algorithm IDs, then records decisions in `coex_dm_8192e_2ant` and observations in `coex_sta_8192e_2ant`.

## State And Persistence
All declared state is plain C data with no locking or ownership annotations in the header. Persistence is by module/global storage in the implementation: previous/current fields survive across notifications and periodic ticks until init, IPS, halt, or reset paths rewrite them. Register backup fields are intended to preserve pre-coexistence Wi-Fi retry/rate/AMPDU settings so normal mode can restore them.

## Dependencies And Integration Points
The header assumes kernel integer/bool types, `BIT*` macros, `struct btc_coexist`, and `struct seq_file` are available from the surrounding rtlwifi coexistence include stack. It is included through `halbt_precomp.h`/chip dispatch code and pairs specifically with `halbtc8192e2ant.c`.

## Risks
The state structures expose many tightly coupled fields without helper accessors, making drift between declarations and implementation easy. The declared `ex_btc8192e2ant_stack_operation_notify()` lacks an implementation in the companion file inspected for this work item, which is a build/API risk if referenced. The C2H history arrays are fixed at 10 bytes and require callers/implementation to bound incoming report length. Because the header does not describe locking, any future multi-adapter or concurrent notification path must handle serialization externally.

## Test Signals
Compile coverage should verify all declared exported functions used by dispatch tables resolve. Runtime debug output should reflect coherent `coex_dm` and `coex_sta` fields after init, BT-info notifications, IPS/LPS transitions, and halt. Boundary tests should include malformed or maximum-length BT-info reports to ensure the fixed history buffers are not overrun by the caller/implementation contract.
