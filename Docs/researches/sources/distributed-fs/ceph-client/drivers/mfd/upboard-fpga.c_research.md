# sources/distributed-fs/ceph-client/drivers/mfd/upboard-fpga.c

## Purpose
`upboard-fpga.c` is the MFD core for the FPGA found on UP Board platforms. The FPGA exposes platform ID, firmware ID, pinmux/GPIO-enable, GPIO-direction, LED, and pin-control functions through a simple GPIO-bit-banged register protocol. The driver provides a regmap over that protocol and registers pinctrl and LED children.

## Important APIs, Types, And Functions
Low-level regmap bus callbacks are `upboard_fpga_read()` and `upboard_fpga_write()`, which clock address and data bits over `clear`, `strobe`, `datain`, and `dataout` GPIOs. Access tables and regmap configs are split between original UP and UP2-style FPGA layouts: `upboard_up_regmap_config` and `upboard_up2_regmap_config`. Platform data objects are `upboard_up_fpga_data` and `upboard_up2_fpga_data`. Setup helpers are `upboard_fpga_gpio_init()`, `upboard_fpga_get_firmware_version()`, and `upboard_fpga_version_show()`. `upboard_fpga_probe()` performs platform initialization and child registration.

## Control Flow
Probe allocates `struct upboard_fpga`, reads ACPI match data, initializes a custom regmap with the matched config, obtains all common GPIOs, enables the FPGA, reads platform/manufacturer ID and firmware ID, rejects unsupported manufacturers or major firmware revisions, and registers `upboard-pinctrl` and `upboard-leds` MFD children. Each regmap read clears the transaction, shifts out a 7-bit address plus read flag, then clocks in 16 data bits from `dataout`. Each write clears the transaction, shifts out address bits, then shifts out 16 data bits on `datain`. A read-only sysfs attribute reports parsed firmware major/minor/patch/build fields.

## State, Persistence, And Dependencies
Runtime state includes GPIO descriptors, matched FPGA type/config, regmap pointer, and cached firmware version. No regcache is used (`REGCACHE_NONE`), so every child access performs live GPIO transactions. Persistent hardware effects are writes to function-enable, GPIO-enable, and GPIO-direction registers. Dependencies include ACPI device IDs, gpiod consumer APIs, regmap custom callbacks, bitfield helpers, MFD core, sysfs attribute groups, and UP Board register definitions.

## Integration Points
ACPI IDs `"AANT0F01"` and `"AANT0F04"` select UP2 and original UP register access policies. Child drivers `upboard-pinctrl` and `upboard-leds` consume the shared regmap and FPGA metadata from `struct upboard_fpga`. Regmap access tables prevent children from reading or writing registers outside the model-specific readable/writable ranges. The sysfs attribute is attached through the platform driver's `dev_groups`.

## Risks
GPIO bit-banging uses `gpiod_set_value()` rather than cansleep variants, so GPIO providers must be safe in this context. There is no explicit transaction lock in the read/write callbacks; regmap serialization normally protects callers, but any bypass would corrupt bit streams. Probe always registers `upboard_up_mfd_cells` even for UP2 data, which is fine only if children adapt by FPGA type/regmap ranges. Unsupported firmware major versions reject the whole device; minor/patch compatibility is assumed. The manufacturer check masks only the low byte of platform ID. Timing is implicit in GPIO operations and may be sensitive to GPIO controller behavior.

## Test Signals
Bring-up tests should cover both ACPI IDs, verify GPIO acquisition and enable sequencing, read platform and firmware IDs, and confirm sysfs version formatting. Regmap tests should read all allowed ID/control ranges and reject out-of-range accesses for UP and UP2 configs. Child tests should exercise pinctrl and LED operations through the bit-banged regmap. Negative tests should simulate wrong manufacturer ID, unsupported major firmware, GPIO acquisition failures, and malformed dataout reads.
