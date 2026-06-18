# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/def.h

## Purpose
Provides small RTL8723BE constants shared across descriptor, hardware, and PHY code: channel offset values, RX queue id, chip-version bits, queue selector encodings, and descriptor rate ids.

## Important APIs, Types, And Functions
`enum rtl_desc_qsel` maps software traffic categories and special queues to descriptor queue selector values such as BK, BE, VI, VO, beacon, high, management, and command. `enum rtl_desc8723e_rate` assigns hardware descriptor rate ids for CCK, OFDM, and HT MCS0-MCS15 rates. Macros such as `CHIP_8723B`, `NORMAL_CHIP`, `CHIP_VENDOR_SMIC`, `EXT_VENDOR_ID`, and `RX_MPDU_QUEUE` are consumed by chip detection, PCI ring setup, and rate/power code.

## Control Flow
No direct control flow. These constants shape switch statements in TX descriptor filling, rate-mask construction, chip-version parsing, PHY TX-power programming, and channel-width handling.

## State And Persistence
No mutable state. The enum values are persistent ABI-like values between driver software and RTL8723BE hardware/firmware.

## Dependencies And Integration Points
Included by `dm.c`, `fw.c`, `hw.c`, `phy.c`, and descriptor code. Rate ids are shared with PHY TX-power routines and TX descriptor construction, so changes affect both firmware rate adaptation and direct BB TXAGC programming.

## Risks
Queue selector or rate-id changes are high risk because they alter the wire contract with descriptors and firmware. Chip bit masks must match `REG_SYS_CFG*` layout; bad masks can pick wrong board-specific paths or RF assumptions.

## Test Signals
Check correct queue mapping for AC traffic and management frames, valid rate reporting under CCK/OFDM/HT traffic, and chip-version logs identifying RTL8723B/NORMAL/SMIC attributes correctly during probe.
