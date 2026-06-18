# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.h

## Purpose
`cpsw_sl.h` declares the CPGMAC_SL abstraction used to configure TI Ethernet MAC sliver blocks independently from CPSW front-end details.

## Important APIs, Types, And Functions
`enum cpsw_sl_regs` defines logical sliver registers such as IDVER, MACCONTROL, MACSTATUS, SOFT_RESET, RX_MAXLEN, pause, EMCONTROL, priority map, and TX gap. The control-bit enum defines MACCONTROL functions including full duplex, loopback, flow control, GMII, gigabit, XGMII, command idle, interface control, external control, CRC options, and error-frame copy controls. The public API declares object creation, reset, control set/clear/reset, idle wait, and logical register read/write.

## Control Flow
The header has no runtime logic, but its enum values are used by `cpsw_sl.c` to index per-SoC register maps and by CPSW open/link code to program port behavior.

## State And Persistence
It forward-declares opaque `struct cpsw_sl`, preserving implementation-private mapping state. Hardware register contents persist in the sliver block until reset or reprogrammed.

## Dependencies And Integration Points
It includes `linux/device.h` and is consumed by CPSW common initialization and port/link setup. It decouples CPSW drivers from SoC-specific sliver MMIO offsets.

## Risks
Adding enum members requires updating every register map in `cpsw_sl.c`; otherwise new logical registers may index uninitialized data. Control bits must match hardware MACCONTROL definitions across variants, and unsupported bits must be captured in feature masks.

## Test Signals
Build and runtime tests should verify all declared logical registers map correctly for supported SoCs, and that link changes produce expected MACCONTROL bits through `cpsw_sl_ctl_set()`/`clr()` without unsupported-bit errors.
