# sources/distributed-fs/ceph-client/drivers/clk/meson/vid-pll-div.h

Purpose: This header declares the descriptor for Meson video PLL fractional divider clocks and the read-only ops table implemented in `vid-pll-div.c`.

Important APIs, types, and functions: `struct meson_vid_pll_div_data` contains two `struct parm` fields: `val` for the fractional shift value and `sel` for the shift selector. It declares `meson_vid_pll_div_ro_ops`.

Control flow: There is no executable logic in the header. SoC clock descriptions provide register field metadata, and the C file uses it during CCF recalc-rate callbacks.

State and persistence behavior: The structure is static clock metadata. Runtime state is the hardware register contents addressed by `val` and `sel`.

Dependencies and integration points: It includes `linux/clk-provider.h` and Meson `parm.h`. It is used by Meson peripheral clock controller files that include video PLL divider stages.

Risks and edge cases: Consumers only get read-only behavior; attempts to use it where software must program the video PLL divider will not be sufficient. Incorrect field widths or offsets will decode to the wrong ratio or zero. Test signals include compile-time inclusion and display clock recalc checks on users such as S4.
