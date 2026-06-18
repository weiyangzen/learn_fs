# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_tty.c

## Purpose
`bcm_vk_tty.c` exposes VK firmware TTY channels as Linux TTY devices backed by BAR1 circular buffers and BAR0 doorbells/interrupts.

## Important APIs, Types, and Functions
Public integration points are `bcm_vk_tty_init()`, `bcm_vk_tty_exit()`, `bcm_vk_tty_irqhandler()`, `bcm_vk_tty_terminate_tty_user()`, and `bcm_vk_tty_wq_exit()`. TTY operations are `bcm_vk_tty_open()`, `bcm_vk_tty_close()`, `bcm_vk_tty_write()`, and `bcm_vk_tty_write_room()`. `bcm_vk_tty_wq_handler()` drains firmware-to-host buffers into the tty flip buffer, while `bcm_vk_tty_poll()` provides timer polling when IRQ support is not enabled.

## Control Flow
Initialization allocates a dynamic raw tty driver, registers `BCM_VK_NUM_TTY` ports, and creates a single-thread workqueue. Open validates channel readiness from `BAR_CARD_STATUS`, records per-channel BAR offsets, snapshots buffer sizes and indices, and starts a poll timer on first open. The work handler checks card status, skips closed channels, reads firmware `wr` offsets, copies bytes from the `from` circular buffer into the tty flip buffer until the shadow `rd` catches up, pushes the flip buffer, and writes the new read index back to BAR1. TTY writes copy each byte into the `to` circular buffer, advance the shadow write index with wraparound, update BAR1, and ring a TTY doorbell.

## State and Persistence
Per-channel state is stored in `vk->tty[]`: open flag, owning PID, BAR offsets, buffer sizes, shadow read/write indices, and tty port. The timer and workqueue live for the device. State is volatile and reset on close/remove.

## Dependencies and Integration Points
The file depends on Linux TTY core, flip buffers, timers, workqueues, signal delivery, and VK BAR access helpers. It integrates with firmware through fixed BAR1 channel offsets, `BAR_CARD_STATUS` readiness bits, BAR1 circular-buffer registers, and a BAR0 TTY doorbell.

## Risks and Edge Cases
`bcm_vk_tty_write()` does not check available circular-buffer space and can overwrite unread firmware data if user space writes more than firmware has consumed; `write_room()` simply returns `to_size - 1`. The poll timer is device-wide but is deleted on the last close according to the current tty's count, which can be fragile across multiple channels. `kill_pid(find_vpid(pid), SIGKILL, 1)` assumes recorded PIDs are still meaningful. Invalid firmware write offsets are logged but do not close the TTY.

## Test Signals
Test open refusal when channel readiness is absent, byte ordering through both circular buffers, wraparound reads and writes, multiple TTY channels, timer and IRQ-driven receive paths, close/remove races with pending work, and large user writes that exceed ring capacity.
