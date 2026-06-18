# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson-aux.c

Purpose: auxiliary-bus Meson reset provider for Amlogic audio clock controller children that share a parent regmap.

Important APIs/types/functions: `meson_reset_aux_ids[]` maps auxiliary names to `struct meson_reset_param`; `meson_reset_aux_probe()` gets the parent regmap and calls `meson_reset_controller_register()`.

Control flow: an auxiliary device from an Amlogic clock controller binds to a name such as `a1-audio-clkc.rst-a1` or `axg-audio-clkc.rst-sm1`. Probe casts `driver_data` to parameters, fetches `dev_get_regmap()` from the parent, and registers a reset controller using toggle-style Meson ops.

State and persistence: no private register ownership; state is in the shared parent regmap. Per-device allocation is devm-managed by the common registration helper.

Dependencies and integration: depends on `AUXILIARY_BUS`, `REGMAP`, the Meson common module, and clock-controller auxiliary device creation.

Risks and test signals: parent regmap absence returns `-EINVAL`; ID strings must match producers exactly. Test auxiliary probe, namespace import `MESON_RESET`, and audio reset behavior for A1/G12A/SM1 variants.
