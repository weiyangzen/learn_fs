# sources/distributed-fs/ceph-client/drivers/soc/versatile/soc-realview.c

## Purpose
This file implements a platform driver that registers SoC bus information for ARM RealView platforms and exposes decoded syscon core ID attributes.

## Important APIs, Types, And Functions
Important functions are `realview_arch_str`, sysfs show handlers, `realview_soc_socdev_release`, and `realview_soc_probe`. The driver matches RealView EB, PB1176, PB11MP, PBA8, and PBX compatibles.

## Control Flow
Probe gets a syscon regmap from the node's `regmap` phandle, allocates devm SoC attributes, reads the first compatible string as `soc_id`, sets machine/family/custom attributes, registers the SoC device, adds a devm unregister action, reads the core ID register, and logs the core ID and HBI board number.

## State And Persistence
Global `realview_coreid` stores the raw ID for sysfs attributes. The SoC device is unregistered automatically by devm action. Hardware identity comes from syscon offset 0.

## Dependencies And Integration Points
It depends on OF platform binding, syscon/regmap, SoC bus, and builtin platform-driver registration through `SOC_REALVIEW`.

## Risks And Test Signals
Risks include global coreid if multiple devices ever existed, registration before core ID read causing attributes to rely on later state, and `of_property_read_string("compatible")` using only the first compatible string. Test signals include successful probe, SoC bus fields, custom attributes `manufacturer`, `board`, `fpga`, and `build`, and boot log with HBI number.
