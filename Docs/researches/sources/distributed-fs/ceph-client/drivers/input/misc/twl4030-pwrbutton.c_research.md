# sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-pwrbutton.c

## Purpose
`twl4030-pwrbutton.c` supports TWL4030 and TWL6030 PMIC power buttons. It reads a PM_MASTER status register on IRQ and reports the power-button bit as `KEY_POWER`, with TWL6030-specific manual interrupt unmask/mask handling.

## Important APIs, Types, and Functions
`struct twl_pwrbutton_chipdata` describes the status register and whether manual IRQ unmasking is required. `powerbutton_irq()` reads the status register through `twl_i2c_read_u8()` and reports `KEY_POWER`. `twl4030_pwrbutton_probe()` matches chipdata, requests a threaded IRQ, registers input, optionally unmasks TWL6030 interrupts, and marks wakeup. `twl4030_pwrbutton_remove()` masks TWL6030 interrupts.

## Control Flow
Probe gets match data, stores it as platform data, allocates input, requests a rising/falling threaded IRQ, registers input, and then for TWL6030 unmasks line and status interrupt bits. IRQ reads the configured status register, reports key state if the read succeeds, calls `pm_wakeup_event()`, and syncs. Remove masks the manual TWL6030 interrupt bits.

## State and Persistence Behavior
Chipdata is stored as platform driver data. Input core persists key state. TWL6030 interrupt mask register updates persist until remove or another TWL consumer changes them. Device wake capability is recorded but no local suspend wake ops are present.

## Dependencies and Integration Points
Depends on TWL MFD I2C helpers, TWL6030 interrupt mask helpers, OF compatibles `ti,twl4030-pwrbutton` and `ti,twl6030-pwrbutton`, platform IRQs, and input core.

## Risks and Edge Cases
`platform_get_irq()` is called before checking its return and the result is passed to IRQ request without explicit negative handling. If the second TWL6030 unmask fails after the first succeeds, probe returns error with partial unmasking. Remove ignores mask errors. The IRQ reports `value & BIT(0)` directly, which is nonzero rather than normalized to 1.

## Test Signals
Test both compatibles, TWL status read success/failure, TWL6030 unmask/mask paths including partial failure, press/release events, IRQ resource absence, wakeup behavior, and removal cleanup.
