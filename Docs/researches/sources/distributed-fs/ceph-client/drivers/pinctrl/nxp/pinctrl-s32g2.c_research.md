# sources/distributed-fs/ceph-client/drivers/pinctrl/nxp/pinctrl-s32g2.c

Purpose: Supplies NXP S32G2 SIUL2-specific pin identifiers, pin descriptors, MMIO pin ranges, OF match data, PM operations, and the built-in platform driver that binds the generic S32 common pinctrl core to S32G2 hardware.

Important APIs, types, and functions: `enum s32_pins` enumerates MSCR pad ids and IMCR input-select ids, including GPIO ports, QSPI, boot mode, I2C, LIN, USDHC, CAN, JTAG, Ethernet/GMAC/PFE EMAC, FlexRay, FlexTimer, DSPI, LLCE, USB, and SIUL external interrupt inputs. `s32_pinctrl_pads_siul2[]` lists the actual `pinctrl_pin_desc` entries exposed to the core. `s32_pin_ranges_siul2[]` maps sparse pin id ranges to six platform MMIO resources. `s32_pinctrl_data` packages those arrays for the common probe. `s32g_pinctrl_probe()` passes OF match data into `s32_pinctrl_probe()`.

Control flow: The driver is registered with `builtin_platform_driver()`, matching `nxp,s32g2-siul2-pinctrl`. Probe retrieves `s32_pinctrl_data` from the OF match table and delegates all substantive setup to the common S32 core. PM uses `LATE_SYSTEM_SLEEP_PM_OPS(s32_pinctrl_suspend, s32_pinctrl_resume)`, so suspend/resume sequencing is handled by the common code after most device suspend and before most resume actions.

State and persistence: This file itself is immutable SoC description plus platform-driver metadata. Hardware state and parsed DT runtime state live in `pinctrl-s32cc.c`. The memory ranges determine persistence/save-restore behavior because they decide which pin ids can be read or written through the common regmap helpers.

Dependencies and integration points: Depends on `pinctrl-s32.h`, the common S32CC object, OF/platform driver infrastructure, and a device tree node compatible with `nxp,s32g2-siul2-pinctrl` that provides one MMIO resource per `s32_pin_ranges_siul2` entry and child function/group nodes using the common `pinmux` format.

Risks: The enum values are sparse hardware register indices, not dense array offsets; the `s32_pinctrl_pads_siul2[]` contents and `s32_pin_ranges_siul2[]` must remain consistent with platform resources. Missing enum entries in the pins array make otherwise valid pinmux cells fail common range or descriptor checks. Incorrect range boundaries can cause common regmap offset calculation to target the wrong SIUL2 resource. Because the driver is built-in, Kconfig/Makefile changes must preserve built-in registration semantics.

Test signals: Build/link with `CONFIG_PINCTRL_S32G2=y`, OF probe for `nxp,s32g2-siul2-pinctrl`, successful mapping of six resources, pinctrl debug output listing MSCR and IMCR pins, DT muxing for representative peripherals from both SIUL2_0 and SIUL2_1 ranges, invalid-pin DT rejection, and system suspend/resume preserving owned pins through the common PM callbacks.
