# sources/distributed-fs/ceph-client/drivers/clk/meson/meson-aoclk.h

## Purpose
Declares the shared data contract for Meson always-on clock controller drivers. It lets SoC-specific AO clock files describe both clock-provider data and reset-controller metadata in a single structure consumed by `meson_aoclkc_probe()`.

## Important APIs, Types, And Functions
`struct meson_aoclk_data` embeds `const struct meson_clkc_data clkc_data`, then adds `reset_reg`, `num_reset`, and `reset` bit mapping. `struct meson_aoclk_reset_controller` wraps a `reset_controller_dev`, a pointer back to the immutable AO data, and the syscon `regmap`. `meson_aoclkc_probe(struct platform_device *pdev)` is the public helper prototype exported by the implementation.

## Control Flow
There is no runtime control flow in the header. Its layout is nevertheless part of the control path: implementation code uses `container_of(clkc_data, struct meson_aoclk_data, clkc_data)`, so `clkc_data` must remain embedded with stable type and identity in every SoC data object.

## State And Persistence
The header defines the software state shape for reset registration and immutable SoC metadata. Hardware state remains in syscon registers identified by `reset_reg` and by the clock data described through `meson_clkc_data`.

## Dependencies And Integration Points
Includes Linux clock provider, platform-device, regmap, and reset-controller headers plus local `clk-regmap.h` and `meson-clkc-utils.h`. SoC files such as `gxbb-aoclk.c` include this header and expose compatible-specific data through OF match tables. The reset framework consumes `reset_controller_dev`; CCF consumes the embedded `meson_clkc_data`.

## Risks And Edge Cases
Any change to `struct meson_aoclk_data` must preserve the `container_of` relationship used by the implementation. Reset arrays are raw bit maps, so signedness and count mismatches can become register writes to the wrong reset line. Header consumers also depend on the `CLK_MESON` exported probe symbol being available.

## Test Signals
Compile all Meson AO drivers that include this header, with namespace imports enabled. Static review should verify each `struct meson_aoclk_data` supplies `.clkc_data`, `.reset_reg`, `.num_reset`, and `.reset` consistently with its DT reset binding.
