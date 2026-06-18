# sources/distributed-fs/ceph-client/drivers/reset/amlogic/reset-meson.c

Purpose: OF platform driver for memory-mapped Amlogic Meson reset controllers.

Important APIs/types/functions: SoC parameter structures `meson8b_param`, `meson_a1_param`, `meson_s4_param`, `t7_param`; `meson_reset_dt_ids[]`; MMIO `regmap_config`; and `meson_reset_probe()`.

Control flow: probe maps resource 0, selects match data by compatible string, initializes an MMIO regmap, and delegates registration to `meson_reset_controller_register()`. Compatible strings cover Meson8b/GXBB/AXG, A1, S4/C3, and T7-style layouts.

State and persistence: hardware reset registers persist according to SoC reset block behavior; driver state is devm-managed and recreated on probe.

Dependencies and integration: depends on OF, platform bus, MMIO regmap, reset framework, and Meson common exports.

Risks and test signals: wrong reset count or offsets expose invalid lines or touch wrong registers. Test each compatible, MMIO mapping failure, regmap initialization failure, and client reset phandle translation using the default one-cell mapping.
