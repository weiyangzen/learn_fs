# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-regs.c

## Purpose
`fimc-is-regs.c` implements mailbox/register operations used to communicate with FIMC-IS firmware: clearing interrupts, waiting for firmware mailbox readiness, sending host commands, reading reply arguments, setting ISP buffer masks, and synchronous interface wrappers for parameter and mode changes.

## Important APIs, Types, and Functions
Interrupt helpers include `fimc_is_fw_clear_irq1()`, `fimc_is_fw_clear_irq2()`, and `fimc_is_hw_set_intgr0_gd0()`. Mailbox readiness and argument helpers are `fimc_is_hw_wait_intmsr0_intmsd0()` and `fimc_is_hw_get_params()`. Command helpers include `fimc_is_hw_set_param()`, `fimc_is_hw_set_sensor_num()`, `fimc_is_hw_close_sensor()`, `fimc_is_hw_get_setfile_addr()`, `fimc_is_hw_load_setfile()`, `fimc_is_hw_change_mode()`, `fimc_is_hw_stream_on()`, `fimc_is_hw_stream_off()`, and `fimc_is_hw_subip_power_off()`. Synchronous wrappers are `fimc_is_itf_s_param()` and `fimc_is_itf_mode_change()`.

## Control Flow
Most command helpers wait until interrupt mask/status register 0 indicates the mailbox slot is idle, write a command id and arguments to ISSR registers, then generate host-to-firmware interrupt GD0. `fimc_is_itf_s_param()` optionally copies dirty parameters into the shared region, clears the completion bit, sends `HIC_SET_PARAMETER`, and waits for the IRQ handler to set `IS_ST_BLOCK_CMD_CLEARED`. `fimc_is_itf_mode_change()` sends the scenario command corresponding to `config_index` and waits for `IS_ST_CHANGE_MODE`.

## State and Persistence
State is split between volatile MCUCTL registers and driver state bits in `is->state`. Parameter dirty bitmaps in `is->config` are passed as two ISSR arguments. No persistent storage exists.

## Dependencies and Integration Points
The file depends on inline `mcuctl_read()`/`mcuctl_write()` from `fimc-is.h`, command constants from `fimc-is-command.h`, parameter update helpers from `fimc-is-param.h`, and the core waitqueue/state-bit mechanism in `fimc-is.c`.

## Risks and Edge Cases
`fimc_is_hw_wait_intmsr0_intmsd0()` spins for about 2 ms and returns a timeout, but many command helpers ignore that return value and continue writing registers. `fimc_is_hw_get_params()` limits reads to four arguments, while driver-side reply arrays are larger. `fimc_is_hw_set_isp_buf_mask()` treats a single set bit as not enough buffers and only logs instead of failing. Mode-change command lookup depends on `config_index` staying below the scenario array size.

## Test Signals
Exercise all host commands with firmware present, timeout behavior when the mailbox stays busy, set-parameter completion and not-done paths, mode changes for all four scenarios, stream on/off state bits, setfile address/load handshake, close-sensor id matching, ISP DMA buffer masks, and IRQ clear side effects.
