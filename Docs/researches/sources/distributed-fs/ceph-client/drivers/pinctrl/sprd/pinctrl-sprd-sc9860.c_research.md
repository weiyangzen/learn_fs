# sources/distributed-fs/ceph-client/drivers/pinctrl/sprd/pinctrl-sprd-sc9860.c

## Purpose
This file is the Spreadtrum SC9860 SoC-specific pin table and platform-driver wrapper for the common Spreadtrum pinctrl core. It enumerates the SC9860 global-control, common-pin, and misc-pin register entries, builds a `struct sprd_pins_info` array from that encoded metadata, and binds the common probe/remove/shutdown routines to the `sprd,sc9860-pinctrl` device-tree compatible.

## Important APIs, types, and functions
The key data is `enum sprd_sc9860_pins`, whose entries are packed with `SPRD_PIN_INFO(num, type, offset, width, reg)`, and `sprd_sc9860_pins_info[]`, whose entries are expanded with `SPRD_PINCTRL_PIN()`. `sprd_pinctrl_probe()` calls `sprd_pinctrl_core_probe(pdev, sprd_sc9860_pins_info, ARRAY_SIZE(...))`. `sprd_pinctrl_of_match[]` declares the compatible string, and `sprd_pinctrl_driver` wires `.probe`, `.remove = sprd_pinctrl_remove`, and `.shutdown = sprd_pinctrl_shutdown`.

## Control flow
Module initialization registers a platform driver. On probe, no local register access is performed; the SoC table is passed to the core. The core later interprets the packed metadata to derive MMIO addresses for global control registers, common pin registers, and misc pin registers. Device-tree child groups are parsed by the core, so the SC9860 file only supplies the universe of legal pin names and their encoded register layout.

## State and persistence behavior
This file owns no runtime state. Its static arrays are read-only metadata after initialization. Hardware state persists through the common driver's writes to the controller MMIO registers. Shutdown persistence is delegated to the common `sprd_pinctrl_shutdown()` path, which selects a pinctrl state named `shutdown` if present.

## Dependencies and integration points
It depends on `pinctrl-sprd.h`, `linux/platform_device.h`, and module/of matching infrastructure. It integrates with Linux pinctrl through `sprd_pinctrl_core_probe()` exported by `pinctrl-sprd.c`. It also depends on the SC9860 device tree using pin names identical to the generated enum-token strings such as `SC9860_U0TXD` or `SC9860_SD0_CLK`, because the common parser resolves group pin names by string match.

## Risks
The table is large and manually ordered. Common pins and misc pins are assigned register offsets by the core using the array order minus counts of earlier global/common pins, so reordering entries can silently change hardware addresses. Reserved common/misc pairs are present in the enum but omitted from `sprd_sc9860_pins_info[]`; adding them without checking numbering may expose nonexistent pins. Any typo in a generated pin name breaks device-tree group parsing. The table also has sparse pin numbers, so code must not assume array index equals pin number.

## Test signals
Build coverage should include `CONFIG_PINCTRL_SPRD_SC9860=m/y`. Runtime signals include successful probe for `sprd,sc9860-pinctrl`, correct pin count in debugfs, successful DT group parsing for representative UART/I2C/SD/eMMC/RF pins, and mux/pinconf writes landing at expected SC9860 register offsets. Shutdown state testing should confirm the common driver applies a `shutdown` state when one is declared.
