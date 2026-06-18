# sources/distributed-fs/ceph-client/drivers/reset/amlogic/Kconfig

Purpose: Amlogic Meson reset Kconfig definitions for the shared Meson reset core, MMIO platform reset controller, auxiliary reset controller, and audio arbiter reset block.

Important APIs/types/functions: symbols are `RESET_MESON_COMMON`, `RESET_MESON`, `RESET_MESON_AUX`, and `RESET_MESON_AUDIO_ARB`. The common symbol selects `REGMAP`; platform Meson selects `REGMAP_MMIO`; auxiliary Meson selects `AUXILIARY_BUS`.

Control flow: configuration only. `RESET_MESON` and `RESET_MESON_AUX` both select the shared common implementation that exports `meson_reset_controller_register()` and reset ops.

State and persistence: build state is stored in `.config`; no runtime state.

Dependencies and integration: intended for `ARCH_MESON` or `COMPILE_TEST`. The auxiliary driver integrates with clock-controller-created auxiliary devices, while the platform driver binds OF MMIO nodes.

Risks and test signals: enabling auxiliary or platform code without `RESET_MESON_COMMON` would break symbols, so the `select` clauses are critical. Test module/built-in combinations and namespace imports for `MESON_RESET`.
