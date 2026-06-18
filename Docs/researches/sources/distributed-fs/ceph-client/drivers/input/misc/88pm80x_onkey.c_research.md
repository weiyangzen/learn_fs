# sources/distributed-fs/ceph-client/drivers/input/misc/88pm80x_onkey.c

## Purpose

This platform child driver reports the ONKEY status of Marvell 88PM80x PMICs as `KEY_POWER`. It also enables long-onkey detection and sets the long-press interval through PMIC RTC miscellaneous registers.

## Important APIs, Types, and Functions

`struct pm80x_onkey_info` stores input device, parent PMIC chip, regmap, and IRQ. `pm80x_onkey_handler()` reads `PM800_STATUS_1`, masks `PM800_ONKEY_STS1`, and reports the power key state. `pm80x_onkey_probe()` obtains parent chip/regmap/IRQ, allocates input, requests the PMIC IRQ through `pm80x_request_irq()`, registers input, programs long-onkey bits, and enables wakeup. Remove frees the PMIC IRQ and input device.

## Control Flow

Probe is driven by an MFD platform child named `88pm80x-onkey`. After resource allocation and input setup, the parent PMIC IRQ helper installs a threaded/oneshot handler. Once input is registered, the driver updates `PM800_RTC_MISC4` to enable long-onkey detection and `PM800_RTC_MISC3` to configure an eight-second interval. IRQ handling is level/status based and directly reports current key state.

## State and Persistence Behavior

Software state is limited to resource pointers. Long-onkey enable and interval persist in PMIC registers after probe. Wake behavior is initialized on the platform child and parent PM ops are reused through `pm80x_dev_suspend/resume`.

## Dependencies and Integration Points

It depends on the 88PM80x MFD core, PMIC regmap definitions, PMIC IRQ allocation helpers, platform child devices, and the input subsystem.

## Risks and Edge Cases

The driver uses manual allocation and non-devm input allocation, so every failure path must remain correct. Register update return values for long-onkey configuration are ignored. IRQ status read failure returns `IRQ_NONE`, potentially problematic for PMIC IRQ dispatch. Wakeup depends on parent PM implementation rather than local IRQ wake calls.

## Test Signals

Test missing IRQ/regmap, PMIC IRQ request/free, status read failures, press/release status changes, long-onkey register programming, input registration failure unwind, remove cleanup, and suspend/resume wake behavior through the parent MFD.
