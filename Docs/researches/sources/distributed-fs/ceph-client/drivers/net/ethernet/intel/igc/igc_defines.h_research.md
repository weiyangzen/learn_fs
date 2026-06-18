# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_defines.h

## Purpose
`igc_defines.h` is the low-level hardware contract for the Intel IGC Ethernet driver. It centralizes register bit definitions, masks, timeout constants, descriptor flags, advertised link modes, wake-on-LAN filters, NVM/PHY encodings, TSN/PTP/PTM fields, packet buffer sizing macros, EEE/LTR knobs, and common driver error codes used by the rest of the IGC sources.

## Important APIs, Types, And Constants
This header exports no functions or structs. Its important interfaces are macros consumed by register access code: descriptor alignment requirements `REQ_TX_DESCRIPTOR_MULTIPLE` and `REQ_RX_DESCRIPTOR_MULTIPLE`; register bit groups such as `IGC_CTRL_*`, `IGC_STATUS_*`, `IGC_ICR_*`, `IGC_IMS_*`, `IGC_RCTL_*`, `IGC_TCTL_*`; speed/duplex and advertise values such as `SPEED_2500` and `ADVERTISE_2500_FULL`; NVM values such as `NVM_CHECKSUM_REG`, `NVM_SUM`, and `IGC_EERD_EEWR_MAX_COUNT`; TSN and launch-time fields such as `IGC_TQAVCTRL_*`, `IGC_TXQCTL_*`, `IGC_TXOFFSET_SPEED_*`; PTP/PTM fields such as `IGC_TSYNCRXCTL_*`, `IGC_TSYNCTXCTL_*`, `IGC_PTM_*`; and EEE/LTR fields such as `IGC_IPCNFG_EEE_*`, `IGC_EEER_*`, and `IGC_LTR*`.

## Control Flow
There is no runtime control flow. The file shapes control flow elsewhere by providing the bit tests and register values used in reset, link setup, interrupt handling, ethtool operations, NVM updates, timestamping, TSN offload, and power-management paths.

## State And Persistence
The macros describe state stored in hardware registers, NVM/flash, descriptor rings, and cached driver fields. Values such as WOL masks can persist across suspend behavior through adapter configuration; NVM constants govern checksum and flash commit flows; EEE and LTR definitions affect link power state.

## Dependencies And Integration Points
The header includes `<linux/bitfield.h>` for `BIT`, `GENMASK`, `FIELD_PREP`, and related helpers. It is included by `igc_hw.h`, `igc_mac.h`, and many C files that access MMIO registers through `rd32`/`wr32`. Changes here have wide blast radius because most source files treat these macros as device specification.

## Risks
Wrong masks or shifts can silently program incorrect hardware bits, break link negotiation, corrupt NVM operations, misroute interrupts, or invalidate timestamp/TSN behavior. ABI-sensitive values used by ethtool register dumps and descriptors must remain consistent with hardware manuals and existing userspace expectations.

## Test Signals
Useful signals include successful driver probe/reset, `ethtool -d` register dumps, `ethtool -S` statistics, WOL suspend/resume tests, EEPROM checksum validation, link-mode negotiation at 10/100/1000/2500 Mbps, PTP timestamp tests, TSN qdisc offload tests, and self-tests that exercise register patterns and NVM validation.
