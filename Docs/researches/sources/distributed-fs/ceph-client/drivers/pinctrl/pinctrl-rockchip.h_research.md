# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rockchip.h

## Purpose
This header is the shared contract between the Rockchip pinctrl driver and the Rockchip GPIO-bank driver. It defines logical pin numbers, SoC type identifiers, GPIO register layout descriptions, per-bank pinctrl metadata, mux route/recalculation tables, parsed DT group/function structures, and the top-level controller state. It lets `pinctrl-rockchip.c` own mux/pinconf parsing while `gpio-rockchip.c` owns GPIO and IRQ-bank registration against the same `rockchip_pin_bank` instances.

## Important APIs, Types, And Functions
The first section defines stable logical pin numbers for GPIO banks 0 through 4, each with A/B/C/D groups of eight pins. `enum rockchip_pinctrl_type` names every SoC variant handled by the driver. `struct rockchip_gpio_regs` describes GPIO register offsets for different GPIO IP versions.

`struct rockchip_iomux` records IOMUX flags and offsets. `enum rockchip_pin_drv_type` and `enum rockchip_pin_pull_type` describe hardware encoding families. `struct rockchip_drv` stores per-eight-pin drive metadata. `struct rockchip_pin_bank` is the central per-bank object: it holds MMIO/regmap/clock/IRQ handles, pin numbering, mux/drive/pull descriptors, GPIO-chip and pinctrl-range instances, IRQ-domain state, locks, register-layout pointer, SoC quirk masks, and deferred pinconf entries.

`struct rockchip_pin_ctrl` describes one SoC family, including the bank array, base offsets, route/recalculated mux tables, and calculator callbacks. `struct rockchip_pin_config`, `struct rockchip_pin_group`, and `struct rockchip_pmx_func` represent parsed device-tree pin groups and functions. `struct rockchip_pinctrl` holds the controller-wide regmaps, registered pinctrl descriptor, parsed groups/functions, and the selected SoC control data.

## Control Flow
There is no runtime code in the header, but the data flow is explicit. `pinctrl-rockchip.c` fills `rockchip_pin_ctrl` static instances with `rockchip_pin_bank` arrays. During probe it computes `pin_base`, register offsets, route masks, and recalculation masks inside each bank, then registers pinctrl groups/functions. `gpio-rockchip.c` later finds the same bank objects, maps each bank's GPIO MMIO, registers gpiolib/IRQ state, and drains deferred pin configuration lists stored in `rockchip_pin_bank`.

## State And Persistence
The header defines in-memory state layouts rather than persistence mechanisms. `rockchip_pin_bank` carries both static SoC description fields and mutable runtime fields such as `saved_masks`, `toggle_edge_mode`, `domain`, `gpio_chip`, `grange`, and `deferred_pins`. Hardware persistence is represented indirectly through regmap/MMIO handles and register offsets; suspend state for GPIO IRQ masks lives in fields defined here but is acted on by implementation files.

## Dependencies And Integration Points
The types intentionally bind pinctrl, gpiolib, irqdomain, clock, regmap, and device-tree code. Because the GPIO driver includes this header, field changes in `rockchip_pin_bank` or `rockchip_pinctrl` are cross-driver ABI changes within the kernel tree. The header also encodes assumptions about Rockchip GPIO register naming and about the bank size grouping used by the pinctrl driver, especially the four IOMUX/drive/pull descriptors per bank.

## Risks And Test Signals
The main risk is structural coupling: adding a SoC or altering a field can break either pinctrl or GPIO-bank code. `nr_pins`, `pin_base`, and `nr_banks` must remain consistent or pin-to-bank lookup and GPIO ranges become wrong. Deferred pin configuration requires the list and mutex fields to be initialized before GPIO-bank probe. Test signals include building both Rockchip pinctrl and GPIO drivers together, probing with old and new GPIO register layouts, validating pin numbers and ranges against DT bindings, exercising deferred pinconf handoff, and checking suspend/resume IRQ-mask fields through the GPIO driver.
