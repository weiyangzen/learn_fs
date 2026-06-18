# sources/distributed-fs/ceph-client/drivers/input/misc/tps65219-pwrbutton.c

## Purpose
`tps65219-pwrbutton.c` supports the TI TPS65219 pushbutton. It reports separate push and release IRQs as `KEY_POWER` and configures PMIC registers to unmask the pushbutton interrupt and select pushbutton pin function.

## Important APIs, Types, and Functions
`struct tps65219_pwrbutton` stores device/input and phys string. `tps65219_pb_push_irq()` reports press and wakeup; `tps65219_pb_release_irq()` reports release. `tps65219_pb_probe()` requests IRQs, registers input, clears the interrupt mask, and writes the MFP configuration. `tps65219_pb_remove()` masks the interrupt again.

## Control Flow
Probe gets the parent `struct tps65219`, creates an I2C input device, obtains IRQ 0 and IRQ 1, requests both threaded handlers, registers input, then clears `TPS65219_REG_MASK_INT_FOR_PB_MASK` and configures `TPS65219_REG_MFP_2_CONFIG` for pushbutton mode. Remove sets the interrupt mask and warns on failure.

## State and Persistence Behavior
Driver state is minimal: input pointer, device pointer, phys string. PMIC interrupt-mask and MFP register writes persist after probe until remove or another consumer changes them. Device wake capability is set in the device core.

## Dependencies and Integration Points
Depends on TPS65219 MFD parent data/regmap, platform IDs, platform IRQ resources, input core, and PM wakeup. Userspace observes `KEY_POWER` on the input node.

## Risks and Edge Cases
Return values from post-registration `regmap_clear_bits()` and `regmap_update_bits()` are ignored, so probe can succeed with interrupts still masked or pin function wrong. IRQ get failures collapse to `-EINVAL`. IRQ names use `dev->init_name`, which may be NULL depending on device initialization. No explicit suspend/resume wake management is present.

## Test Signals
Test push/release IRQs, PMIC mask and MFP register writes, ignored regmap failure behavior, remove masking, missing IRQs, wake event delivery, and repeated bind/unbind.
