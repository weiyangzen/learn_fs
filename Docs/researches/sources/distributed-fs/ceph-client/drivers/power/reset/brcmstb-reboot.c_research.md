# sources/distributed-fs/ceph-client/drivers/power/reset/brcmstb-reboot.c

## Purpose
Broadcom STB syscon reboot driver.

## Important APIs, Types, and Functions
global regmap and reset-mask pointer, `struct reset_reg_mask`, `brcmstb_restart_handler()`, and `brcmstb_reboot_probe()`.

## Control Flow
probe reads syscon phandle args as reset-source and master-reset offsets, chooses 40nm/65nm masks by compatible, and registers restart; handler writes source-enable then master-reset masks with readbacks and delays.

## State and Persistence Behavior
global regmap, offsets, and mask data persist after `subsys_initcall`; syscon reset bits persist until hardware reset.

## Dependencies and Integration Points
OF phandle args, syscon/regmap, restart sys-off, Broadcom compatible data.

## Risks and Edge Cases
driver uses globals so multiple instances conflict; readback errors only log; exact phandle arg count and mask data must match binding.

## Test Signals
40nm and 65nm compatibles, bad phandle args, regmap write/read failures, and reboot hardware tests.
