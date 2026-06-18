# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/pinctrl-meson-axg-pmx.h

Purpose: Declares the data structures and macros used by the AXG-generation Meson pinmux implementation. It is the contract between SoC-specific pin table files and `pinctrl-meson-axg-pmx.c`.

Important APIs and types: Defines `struct meson_pmx_bank` with bank name, first/last pin, mux register index, and starting bit offset. Defines `struct meson_axg_pmx_data`, which wraps a mux-bank array and count. Defines `struct meson_pmx_axg_data`, which carries the 4-bit function selector for a group. Macros `BANK_PMX()`, `PMX_DATA()`, `GROUP()`, and `GPIO_GROUP()` build the static objects consumed by `meson_axg_pmx_ops`. The header also declares `extern const struct pinmux_ops meson_axg_pmx_ops`.

Control flow: No executable code is present. The macros expand inside SoC table files to initialize `struct meson_pmx_group` entries and mux-bank data. At runtime the AXG pinmux implementation reads those structures through `pc->data->groups[group_num].data` and `pc->data->pmx_data`.

State and persistence: The header defines immutable table shapes, not runtime state. Its function selector values eventually become persistent hardware mux state when `meson_axg_pmx_ops` writes mux registers.

Dependencies and integration points: It assumes inclusion after common Meson pinctrl definitions and availability of `ARRAY_SIZE`. It is used by AXG-style SoC data files including AXG, G12A, A1, C3, and T7. It intentionally differs from `pinctrl-meson8-pmx.h`, where legacy SoCs use bit-enable mux groups rather than per-pin 4-bit selectors.

Risks: Macro-generated compound literals must remain valid for static initialization patterns used in the SoC files. Any change to `struct meson_pmx_axg_data` or `GROUP()` layout must be synchronized with the cast in `meson_axg_pmx_set_mux()`. Because `BANK_PMX()` table register units are later shifted by `reg << 2`, the unit convention must be documented and preserved. The header lacks include guards in the shown source, so duplicate inclusion in one translation unit would be risky, although current users include it once.

Test signals: Compile all AXG-generation pinctrl drivers. Runtime validation is indirect: successful mux selection for groups created by `GROUP()`, successful GPIO mode for groups created by `GPIO_GROUP()`, and correct mux-bank lookup for every `BANK_PMX()` range.
