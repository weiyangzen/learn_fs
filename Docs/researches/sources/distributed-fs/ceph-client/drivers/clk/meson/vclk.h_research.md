# sources/distributed-fs/ceph-client/drivers/clk/meson/vclk.h

Purpose: This header declares the data structures and ops symbols for Meson reset-aware video-clock gates and dividers.

Important APIs, types, and functions: `struct meson_vclk_gate_data` carries enable and reset `parm` fields plus a flags byte. `struct meson_vclk_div_data` carries divider, enable, reset, optional divider table, and flags. It declares `meson_vclk_gate_ops` and `meson_vclk_div_ops`.

Control flow: The header itself has no executable logic. Clock controller descriptions instantiate these structures as `clk_regmap.data`; `vclk.c` casts them back and uses the register-field metadata in CCF callbacks.

State and persistence behavior: The structures are static per-clock descriptors. They point the implementation at persistent MMIO fields for divider, enable, and reset state. There is no runtime allocation or cache in the header contract.

Dependencies and integration points: It includes `clk-regmap.h` and `parm.h`. It is intended for Meson display/video clock tree definitions that need reset-aware gate or divider behavior but still integrate through common `clk_regmap` registration.

Risks and edge cases: Users must describe reset bits accurately and set divider tables/flags consistently with CCF divider encoding. The documented `flags` semantics mention clk-gate and clk-divider flags, but unsupported flags such as HIWORD masks are ignored by the implementation. Test signals are compile-time users plus runtime register traces for gate/divider enable and disable.
