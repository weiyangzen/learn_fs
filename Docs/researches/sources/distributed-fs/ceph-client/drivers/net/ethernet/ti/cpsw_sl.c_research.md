# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_sl.c

## Purpose
`cpsw_sl.c` implements the CPGMAC_SL, or MAC sliver, abstraction used by CPSW and related TI Ethernet devices. It maps logical sliver registers and supported MAC control bits across device variants and provides reset, register access, MAC control set/clear, and idle wait helpers.

## Important APIs, Types, And Functions
`struct cpsw_sl` stores device, MMIO base, selected register map, supported control feature mask, and idle mask. `struct cpsw_sl_dev_id` describes per-device register maps, offset adjustment, supported control bits, and idle mask. Public exported APIs are `cpsw_sl_get()`, `cpsw_sl_reg_read()`, `cpsw_sl_reg_write()`, `cpsw_sl_reset()`, `cpsw_sl_ctl_set()`, `cpsw_sl_ctl_clr()`, `cpsw_sl_ctl_reset()`, and `cpsw_sl_wait_for_idle()`.

## Control Flow
`cpsw_sl_get()` allocates a managed sliver object, matches `device_id`, assigns the register map and feature masks, and applies per-device base offset. Register read/write reject unsupported logical registers. Reset writes the soft-reset bit and polls until it clears or times out. Control set/clear validates requested bits against `control_features`, reads MACCONTROL, modifies bits, and writes back. Idle wait polls MACSTATUS until the configured idle mask is set.

## State And Persistence
The sliver object persists as devm-managed per-slave state under `struct cpsw_slave`. Hardware state persists in MACCONTROL, MACSTATUS, reset, maxlen, pause, priority map, and other sliver registers. `control_features` prevents unsupported controls from being written for a selected SoC.

## Dependencies And Integration Points
It depends on MMIO, kernel delay/jiffies, and `cpsw_sl.h`. CPSW open/link paths use it to reset ports, set RX max length, priority maps, GMII/gigabit/full-duplex/flow-control bits, and wait for idle on link down.

## Risks
Unsupported logical register reads return 0 after logging, which may hide configuration errors if callers do not check device capabilities. `cpsw_sl_ctl_set()` and `_clr()` return `u32` but can return negative errno values, so caller typing is awkward. Timeout loops rely on correct idle/reset bit definitions per SoC. Wrong `device_id` mapping or `regs_offset` will direct all MAC programming to the wrong MMIO locations.

## Test Signals
Test sliver reset and idle wait on each supported `device_id`, verify unsupported register logging, validate MACCONTROL bits during link speed/duplex/pause transitions, and check that AM65/K3 idle mask requirements work on link down and suspend/resume.
