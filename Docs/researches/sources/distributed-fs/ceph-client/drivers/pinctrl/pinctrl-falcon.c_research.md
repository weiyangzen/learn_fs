# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-falcon.c

## Purpose

This file implements pinctrl and pin configuration support for Lantiq Falcon SoCs. It uses the shared Lantiq pinctrl framework from `pinctrl-lantiq.h` for most generic mux/group/function handling, while this file supplies Falcon-specific pad register offsets, MFP tables, groups, functions, pinconf operations, pad-bank discovery, and mux application.

The hardware is arranged as up to five banks/ports of 32 pins. Each bank has mux registers per pin plus pull-up, pull-down, slew-rate, drive-current, and availability registers.

## Important APIs, Types, and Data

- Register macros include `LTQ_PADC_MUX(x)`, `LTQ_PADC_PUEN`, `LTQ_PADC_PDEN`, `LTQ_PADC_SRC`, `LTQ_PADC_DCC`, and `LTQ_PADC_AVAIL`.
- `PORTS`, `PINS`, `PORT(x)`, and `PORT_PIN(x)` map global GPIO numbers to pad bank and in-bank bit positions.
- `enum falcon_mux` defines Falcon mux function IDs, including GPIO, reset, NTR/PPS, MDIO, LED, SPI, ASC, I2C, HOSTIF/JTAG, SLIC/PCM, MII, PHY, and `NONE`.
- `falcon_pads` and `pad_count` are static arrays populated at probe from hardware availability registers.
- `falcon_mfp` lists each mux-capable pin and its function choices using `MFP_FALCON`.
- `falcon_grps` declares named pin groups such as `por`, `mdio`, `bootled`, `asc0`, `spi`, `i2c`, `jtag`, `slic`, `pcm`, and `asc1`.
- `falcon_funcs` maps external pinmux function names to group lists.
- `falcon_cfg_params` maps device-tree properties `lantiq,pull`, `lantiq,drive-current`, and `lantiq,slew-rate` to Lantiq pinconf parameters.
- Exported helpers `pinctrl_falcon_get_range_size()` and `pinctrl_falcon_add_gpio_range()` support Falcon GPIO drivers.

## Control Flow

The platform driver is registered through `core_initcall_sync(pinctrl_falcon_init)`, so it initializes early. `pinctrl_falcon_probe()` scans all enabled device-tree nodes compatible with `"lantiq,pad-falcon"`. For each valid bank, it reads `lantiq,bank`, translates the MMIO resource, gets the bank clock from that pad platform device, maps the pad registers, reads `LTQ_PADC_AVAIL`, computes the number of pins with `fls(avail)`, loads pin descriptors named `ioN`, enables the clock, and accumulates the total pin count.

After bank discovery, probe fills `falcon_pctrl_desc.name` and `.npins`, attaches Falcon MFP/group/function arrays to `falcon_info`, then calls `ltq_pinctrl_register()`. The shared Lantiq core consumes `falcon_info`, including `apply_mux`, params, groups, and functions.

Mux writes are performed by `falcon_mux_apply()`, which validates the bank and writes the selected mux value to the pin-specific mux register. Pin configuration callbacks read and write per-port bit registers. `falcon_pinconf_get()` returns drive-current, slew-rate, or pull state. `falcon_pinconf_set()` selects the target register and writes the pin bit.

Debug output prints port, raw mux register value, pull, drive-current, slew-rate, and optional GPIO owner.

## State and Persistence Behavior

Driver state is primarily static global `falcon_info`, `falcon_pads`, and `pad_count`, plus MMIO mappings and clocks discovered at probe. Pin descriptors allocate names with `kasprintf()` in `lantiq_load_pin_desc()` and are not explicitly freed, which is acceptable for a non-removable early SoC driver but would matter for hot-unplug style reuse.

Pad configuration is persistent in hardware registers until reset or later reconfiguration. There is no removal path, clock disable path, suspend/resume replay, or explicit locking around pad register read/write operations in this file.

## Dependencies and Integration Points

- Shared Lantiq pinctrl infrastructure in `pinctrl-lantiq.h`, especially `struct ltq_pinmux_info`, `ltq_pinctrl_register()`, MFP parsing, and Lantiq pinconf packing.
- Lantiq SoC low-level register helpers from `<lantiq_soc.h>`.
- Device tree nodes compatible with `"lantiq,pinctrl-falcon"` and child/peer pad nodes compatible with `"lantiq,pad-falcon"` carrying `lantiq,bank`.
- GPIO drivers use `pinctrl_falcon_get_range_size()` and `pinctrl_falcon_add_gpio_range()` to integrate GPIO ranges with the pinctrl device.
- Clock framework is used for each pad bank clock.

## Risks and Edge Cases

- Probe uses the big-endian `lantiq,bank` property value directly as `*bank` without an explicit `be32_to_cpup()`. This may be intentional for this tree's conventions, but it is a notable endian-sensitive pattern.
- `falcon_pinconf_set()` writes only `BIT(PORT_PIN(pin))` to the selected config register. For pull configuration, switching pull direction does not explicitly clear the opposite pull register, and an argument other than `1` selects pull-up.
- `falcon_pinconf_set()` verifies the bit became set, but it cannot express disabling drive-current, slew-rate, or pull with the current write-only pattern.
- Group pinconf get/set return `-ENOTSUPP`; group-level pinconf requests in device tree will fail.
- Static globals make this driver effectively single-instance.
- `lantiq_load_pin_desc()` allocates pin names without checking allocation failure.
- Bank clocks are enabled but not disabled on later failures or module unload; this matches early SoC-driver style but is a resource-management limitation.

## Test Signals

- Probe should log discovered pad banks and total pad count; absence of banks means no useful pinctrl registration.
- Device-tree mux states for ASC, SPI, I2C, MDIO, reset, LED, SLIC, PCM, and JTAG should result in expected `LTQ_PADC_MUX()` values.
- Pinconf reads after applying `lantiq,pull`, `lantiq,drive-current`, and `lantiq,slew-rate` should report expected packed values.
- GPIO range size should match `fls(LTQ_PADC_AVAIL)` for each bank.
- Debugfs pinconf output should show the correct port, mux value, pull, drive-current, slew-rate, and GPIO owner.
