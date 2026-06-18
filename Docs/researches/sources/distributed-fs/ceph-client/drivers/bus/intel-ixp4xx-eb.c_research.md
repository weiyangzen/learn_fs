# sources/distributed-fs/ceph-client/drivers/bus/intel-ixp4xx-eb.c

Purpose: configures the Intel IXP4xx external expansion bus chip-select timing registers from device tree, handles SoC-specific quirks for IXP42x/43x/45x/46x, and populates children attached to the expansion bus.

Important APIs and types: `struct ixp4xx_eb` stores regmap, base address, and variant flags. `ixp4xx_exp_tim_props[]` maps DT timing properties to bitfields. `ixp4xx_exp_setup_child()` computes used chip-select sizes from child `reg`; `ixp4xx_exp_setup_chipselect()` reads/modifies/writes CS timing and recurses over adjacent chip selects for large windows.

Control flow: probe gets a syscon regmap from the bus node, reads CNFG0 to determine boot versus normal bus base, logs IXP43x fuse speed, walks children, configures chip selects, then calls `of_platform_default_populate()` if children exist. Each chip select preserves unspecified boot defaults, rounds size to supported powers of two, applies property values with caps, sets cycle type, masks variant-specific bits, and enables the chip select.

State and persistence: hardware CS timing/config registers are modified; no in-memory state beyond probe. Child devices persist in the device model until unbound.

Dependencies and integration: depends on syscon/regmap, OF child parsing, bitfield helpers, and platform population. It integrates with memory-mapped devices behind the legacy expansion bus.

Risks: invalid DT sizes or chip-select indexes are logged but not fatal to the whole probe. Recursive setup for windows larger than one stride assumes contiguous chip-select joining. Some bits are dangerous on certain variants and are deliberately masked or only logged. Test signals include all compatible variants, boot/normal base detection, timing property bounds, large device windows crossing CS boundaries, illegal cycle type, child population, and regmap read/write failures.
