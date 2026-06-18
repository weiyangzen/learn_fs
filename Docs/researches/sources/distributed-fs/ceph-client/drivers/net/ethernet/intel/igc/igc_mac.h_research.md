# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_mac.h

## Purpose
`igc_mac.h` declares the generic MAC helper interface and management-mode enum used by hardware setup, main driver code, and ethtool paths.

## Important APIs, Types, And Functions
It declares MAC helpers for PCIe master disable, copper link checking, flow-control configuration, receive address initialization, link setup, hardware counter clearing, NVM auto-read completion, semaphore release, RAR programming, collision-distance programming, speed/duplex reporting, management pass-through detection, and multicast address list updates. It also defines `enum igc_mng_mode` values for no management, ASF, pass-through, IPMI, and host-interface-only modes.

## Control Flow
The header contains declarations only. The function set describes the expected MAC control flow: reset paths disable master and wait for NVM auto-read, init paths program RAR and multicast filters, link paths resolve flow control and speed, and management paths inspect firmware mode.

## State And Persistence
Declared functions mutate hardware registers and cached `struct igc_hw` MAC/flow-control state. The header itself stores no state.

## Dependencies And Integration Points
It includes `igc_hw.h`, `igc_phy.h`, and `igc_defines.h`, creating a shared contract among `igc_mac.c`, `igc_base.c`, `igc_main.c`, and ethtool. The prototypes are used both directly and through `struct igc_mac_operations`.

## Risks
Because this header participates in circular-looking hardware includes, changes should preserve include guards and forward declarations. Prototype changes can break operation table assignments and reset/link code. New MAC helpers should keep generic versus I225-specific boundaries clear.

## Test Signals
Build coverage, reset/link setup, flow-control ethtool changes, multicast/RAR programming, management pass-through behavior, and counter clear/update paths validate this interface.
