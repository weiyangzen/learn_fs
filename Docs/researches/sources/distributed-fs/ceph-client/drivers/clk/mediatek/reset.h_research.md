# sources/distributed-fs/ceph-client/drivers/clk/mediatek/reset.h

Purpose: `reset.h` declares the MediaTek clock-reset descriptor format and the registration API used by MediaTek clock-controller drivers.

Important APIs and types: it defines `RST_NR_PER_BANK` as 32 and exposes INFRA reset set-register offsets used by SoC descriptors. `enum mtk_reset_version` distinguishes `MTK_RST_SIMPLE` from `MTK_RST_SET_CLR`. `struct mtk_clk_rst_desc` describes hardware version, reset bank offsets, bank count, optional reset index map, and map length. `struct mtk_clk_rst_data` is the runtime container for regmap, `reset_controller_dev`, and descriptor. The exported function is `mtk_register_reset_controller_with_dev()`.

Control flow: the header has no executable flow. Its descriptors drive `reset.c`, where the selected version chooses reset ops and optional `rst_idx_map` changes DT phandle translation from direct IDs to mapped reset bits.

State and persistence: descriptor arrays are static SoC data. Runtime state is allocated by the reset registration implementation and hardware reset state lives in the controller registers.

Dependencies and integration points: it depends on Linux reset-controller and type headers. It is included by `clk-mtk.h` so `struct mtk_clk_desc` can carry an optional reset descriptor, tying clock and reset provider setup together.

Risks: `rst_bank_ofs` and `rst_idx_map` are mutable pointer types even though they describe static tables; accidental modification would affect all reset users. The comment for `mtk_register_reset_controller_with_dev()` refers to `np` while the parameter is `dev`, a documentation drift but not a behavior issue. Incorrect map lengths or offsets can expose invalid resets to device tree consumers.

Test signals: compile-test SoC descriptors, inspect `/sys/kernel/debug/reset` where available, verify reset phandle translation for mapped controllers, and check that clock-controller probe registers resets only when a descriptor is provided.
