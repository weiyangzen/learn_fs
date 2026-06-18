# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/def.h

## Purpose
`def.h` contains RTL8723AE chip identity macros, RF/power enums, descriptor queue/rate constants, PHY status layout, and H2C command description types.

## APIs, Types, And Constants
Important macros extract chip version fields (`GET_CVID_*`, `IS_8723_SERIES`, cut/vendor/RF type tests), define queue selectors (`QSLT_*`), and enumerate RTL8723E descriptor rates from CCK through MCS32. Enums cover RF operation, RF power state, power-save mode and policy, PCI interface selection, queue selection, and rates. Structs describe CCK PHY status and generic H2C command metadata.

## Control Flow, State, And Persistence
There is no runtime flow. Constants steer later control flow in firmware commands, RF setup, TRX descriptor packing, and chip-cut conditional logic. Incorrect definitions become persistent hardware behavior through register/descriptor programming.

## Dependencies And Integration Points
The header is used across RTL8723AE DM, FW, PHY, RF, HW, and TRX code. It integrates with mac80211 queueing/rate concepts, firmware H2C command paths, and chip version values from hardware/EFUSE reads.

## Risks And Test Signals
Risks include wrong chip-cut detection, rate-code mismatch, queue selector mistakes, or PHY status layout drift. Signals are correct probe classification, association at legacy and HT rates, queue QoS behavior, firmware command construction, and RX signal parsing.
