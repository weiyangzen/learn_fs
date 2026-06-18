# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/def.h

## Purpose
RTL8188EE/related Realtek definitions for chip-version bits, loopback/RF/power/interface enums, descriptor queue selectors, descriptor rate IDs, CCK PHY status, and H2C command metadata.

## Important APIs, Types, And Functions
Macros define prime channel offsets, RX queues, C2H header length, chip bonding extraction, chip/version masks, and predicates such as `IS_81XXC()`, `IS_8723_SERIES()`, `IS_NORMAL_CHIP()`, `IS_1T1R()`, and `IS_2T2R()`. Enums cover chip version, loopback, RF operation, RF power, power policy, PCI interface selection, descriptor queue selection, and descriptor rates. Structs are `phy_sts_cck_8192s_t` and `h2c_cmd_8192c`.

## Control Flow
Chip-specific hardware, PHY, RF, TRX, and firmware files include this header to decode chip version, choose RF/power paths, classify descriptor queues, and encode rates.

## State And Persistence
No storage. Definitions interpret hardware version words, descriptors, received PHY status, and H2C command buffers.

## Dependencies And Integration Points
Consumed by the RTL8188EE object set and aligned with shared rtlwifi queue/rate/power abstractions.

## Risks
Header guard heritage (`__RTL92C_DEF_H__`) shows cross-chip reuse. Bit masks and descriptor IDs are hardware ABI. `RF_TYPE_1T1R` is an inverted mask and can be misused.

## Test Signals
Compile RTL8188EE, verify chip-version detection, RF/rate descriptor encoding, queue selector use, CCK status parsing, and H2C construction.
