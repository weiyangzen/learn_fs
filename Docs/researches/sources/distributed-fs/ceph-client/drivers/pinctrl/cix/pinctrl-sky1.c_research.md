# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/pinctrl-sky1.c

Purpose: Defines the CIX Sky1 pin controller pad/function tables and registers a platform driver for the normal and S5 pinmux domains. It is mostly SoC data: two compatible strings select either the 66-pin S5 pad table or the 138-pin main pad table.

Important APIs and types: Uses `SKY_PINFUNCTION()` entries over `struct sky1_pin_desc`, packages them as `sky1_pinctrl_soc_info`, and calls the shared `sky1_base_pinctrl_probe()`. Runtime PM hooks use `pinctrl_force_sleep()` and `pinctrl_force_default()`. The `of_device_id` table binds `cix,sky1-pinctrl-s5` and `cix,sky1-pinctrl`.

Control flow: `arch_initcall()` registers the platform driver. Probe retrieves match data with `device_get_match_data()` and delegates all controller setup to the shared base driver. Suspend/resume look up `struct sky1_pinctrl` from driver data and force hog sleep/default states through the pinctrl core.

State and persistence: The file stores immutable pad/function arrays. Runtime state is in the base driver allocation and in hardware registers managed by that base implementation. Selected pin states persist in controller registers until later state changes, suspend/resume, or reset.

Dependencies and integration points: Depends on the generic pinctrl core, OF platform matching, and `pinctrl-sky1.h`. It integrates with board DT pinctrl references, CIX GPIO/peripheral consumers, and the shared Sky1 base implementation not shown here.

Risks: Pad data is table-driven and easy to misalign with hardware numbering. Several pins intentionally expose empty function lists for fixed/system signals, so DT must not request alternate functions there. The source as read contains duplicate-looking table entries in the main domain; build and runtime pin-list inspection should catch unintended duplication or numbering drift.

Test signals: Build the Sky1 pinctrl driver, boot with both compatible strings, inspect `/sys/kernel/debug/pinctrl`, select default and sleep states, and exercise I2C/I3C, SPI, UART, I2S/HDA, GMAC, USB, and GPIO pins from DT.
