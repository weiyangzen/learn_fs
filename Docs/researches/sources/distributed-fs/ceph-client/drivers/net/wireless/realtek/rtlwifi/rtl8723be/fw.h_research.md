# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/fw.h

## Purpose
Defines RTL8723BE firmware constants, RPWM/LPS state bits, H2C command ids, H2C payload packing macros, and public firmware command prototypes.

## Important APIs, Types, And Functions
Firmware size/address constants describe the legacy firmware layout. RPWM macros define RF-on/off, clock-on/off, ACK/toggle, active/register bits, and helpers such as `IS_IN_LOW_POWER_STATE()` and `FW_PS_IS_ACK()`. `enum rtl8723b_h2c_cmd` lists command ids for reserved pages, media status, scan, keepalive, disconnect decision, power mode, LPS parameters, P2P PS offload, RA mask, and RSSI reports. Payload macros set fields for power mode, media status, and reserved-page locations. Public functions are the command helpers implemented in `fw.c`.

## Control Flow
No direct flow, but the macros define how `fw.c` packs mailbox payloads and how `hw.c` interprets firmware power-state transitions.

## State And Persistence
No state is stored here. Constants describe firmware-visible bits and command numbers that persist as ABI with the RTL8723B firmware image.

## Dependencies And Integration Points
Included by `fw.c`, `hw.c`, and dynamic-management code. It ties rtlwifi software power-save state to firmware RPWM/CPWM handshakes and H2C mailbox commands.

## Risks
Duplicated `FW_PWR_STATE_ACTIVE`/`FW_PWR_STATE_RF_OFF` definitions should remain identical but are maintenance noise. Incorrect command ids or bit packing would make firmware ignore or misinterpret power, media, reserved-page, and P2P commands.

## Test Signals
Compile-time macro use, firmware command acceptance, correct LPS state transitions, successful reserved-page location H2C, and RA/RSSI reports reaching firmware are the main signals.
