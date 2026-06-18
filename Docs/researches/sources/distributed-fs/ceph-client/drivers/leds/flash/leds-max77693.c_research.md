# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-max77693.c

## Purpose
This platform driver controls the flash LED block inside the Maxim MAX77693 MFD. It supports one or two FLED outputs, optional joint current-output mode, torch and flash modes, external strobe, fault reporting, and V4L2 flash subdevices.

## Important APIs, Types, and Functions
`struct max77693_led_device` stores parent regmap, mutex, sub-LEDs, current limits, mode flags, allowed modes, current-output mask, and joint-output state. `struct max77693_sub_led` stores per-FLED flash class device, V4L2 handle, brightness/timeout/fault caches, and ID. Key helpers include `max77693_set_mode_reg()`, `max77693_add_mode()`, `max77693_clear_mode()`, `max77693_distribute_currents()`, `max77693_set_torch_current()`, `max77693_set_flash_current()`, `max77693_set_timeout()`, and `max77693_get_flash_faults()`.

## Control Flow
Probe obtains the parent MFD regmap, parses child nodes and `led-sources`, validates/clamps current, timeout, boost, and voltage settings, initializes hardware registers, initializes one or two flash class devices, and registers corresponding V4L2 devices. Torch brightness sets ITORCH and enables torch mode. Flash brightness sets IFLASH registers. Strobe updates timeout if needed, records the strobing LED, enables flash mode, reads faults, and clears flash mode flags after the one-shot programming path.

## State and Persistence
State is volatile and mutex-protected. `mode_flags` tracks active torch/external modes while flash modes are cleared after triggering to avoid repeated strobes. `torch_iout_reg` caches combined torch current register fields. Per-sub-LED timeout and fault fields cache class settings and last fault state. Firmware node references are manually put after registration or errors.

## Dependencies and Integration Points
The driver depends on the MAX77693 MFD parent, MAX77693 register definitions, regmap, OF child nodes with `led-sources`, LED flash class, and optional V4L2 flash class. It binds `maxim,max77693-led` as a platform child of the MFD.

## Risks and Edge Cases
Joint-output mode changes current distribution and allowed modes, so one LED node with two `led-sources` behaves differently from two independent nodes. External flash mode deliberately enables both FLASHEN and TORCHEN hardware pins, which can interfere with software modes if not cleared. Fault mapping treats open faults as over-voltage. Error cleanup must unregister FLED1 if FLED2 registration fails. Boost mode is forced on for joint outputs when firmware requested no boost.

## Test Signals
Test single FLED1, single FLED2, two independent LEDs, and joint-output DT layouts. Validate torch current distribution, flash current splitting, timeout programming, external strobe, boost mode/voltage registers, fault reporting, and remove cleanup. V4L2 tests should confirm unique device names and external strobe support.
