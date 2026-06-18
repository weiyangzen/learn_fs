# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-lochnagar.c

Purpose: Cirrus Lochnagar board pinctrl/GPIO driver supporting Lochnagar1 and Lochnagar2 pin muxes, AIF routing, and output-only GPIO controls.

Important APIs/types/functions: macro-generated pin, AIF, function, and group tables feed `struct lochnagar_pin_priv`. `lochnagar_set_mux()`, `lochnagar_pin_set_mux()`, `lochnagar_aif_set_mux()`, and `lochnagar_conf_group_set()` implement mux and AIF master/slave config. A `gpio_chip` exposes board-control GPIO outputs.

Control flow: probe identifies parent MFD type, selects Lochnagar1/2 tables, builds function-to-group arrays, registers pinctrl, and registers gpiochip. Pin muxing dispatches by function type: pin functions write mux registers, while AIF functions set source/enable bits and for Lochnagar2 force associated mux pins to AIF. GPIO set either routes mux pins through Lochnagar2 GPIO channels or toggles direct GPIO bits.

State and persistence: register writes persist in Lochnagar MFD regmap. Lochnagar2 dynamically allocates up to 16 GPIO channel source registers, reusing existing matching channels or first free channel. The driver itself stores only table pointers and generated group lists.

Dependencies/integration: MFD Lochnagar regmaps and type IDs, DT binding constants, gpiolib, pinctrl, generic pinconf, and pinctrl-utils. Supports `cirrus,lochnagar-pinctrl`.

Risks: `lochnagar_pin_set_mux()` logs regmap write errors but returns 0 at the end, which can hide failed pin mux writes. GPIOs support output only; input direction returns `-EINVAL`. Lochnagar2 GPIO channel exhaustion returns `-ENOSPC`.

Test signals: probe both board revisions, verify function-group membership, route AIF groups and master/slave config, exhaust or reuse Lochnagar2 GPIO channels in tests, and check direct reset GPIO inversion behavior.
