<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h

## Purpose
`status.h` defines the compact register-field layout for WM831x status LED blocks. It gives LED drivers the masks and shifts needed to select source, blink mode, sequence length, duration, and duty cycle.

## Important APIs, types, and functions
There are no functions or structs. Public macros are `WM831X_LED_SRC_MASK/SHIFT/WIDTH`, `WM831X_LED_MODE_MASK/SHIFT/WIDTH`, `WM831X_LED_SEQ_LEN_MASK/SHIFT/WIDTH`, `WM831X_LED_DUR_MASK/SHIFT/WIDTH`, and `WM831X_LED_DUTY_CYC_MASK/SHIFT/WIDTH`.

## Control flow
The status LED child driver combines platform defaults from `wm831x_status_pdata` with LED-class operations, then updates the appropriate status LED register fields using these masks. Hardware can drive LEDs from OTP, power, charger, or manual sources.

## State and persistence behavior
LED mode state is stored in the PMIC LED control registers. Platform data may request preservation of existing hardware state, so probe must avoid overwriting fields when the default source is preserve.

## Dependencies and integration points
The header integrates with `pdata.h` status LED source definitions, Linux LED triggers, and WM831x MFD register access.

## Risks and test signals
Risks include overwriting preserved OTP settings, using raw enum values without accounting for register encoding, and applying blink timing masks to the wrong bits. Test signals include LED trigger registration, manual brightness updates, boot-preserve behavior, and charger/power-source LED source selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm831x/status.h -->
