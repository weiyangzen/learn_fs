# sources/distributed-fs/ceph-client/drivers/clk/at91/dt-compat.c

Purpose: legacy device-tree compatibility layer that registers individual AT91 clock nodes using older compatible strings, forwarding each node to the newer common provider helpers.

Important APIs and data: numerous `CLK_OF_DECLARE` setup functions cover audio PLL, generated clocks, H32MX, I2S mux, main oscillators, main clocks, master clocks, peripherals, PLLs, PLL dividers, programmable clocks, slow clock, SMD, system clocks, USB, and UTMI. Helper parsers allocate master and PLL characteristics from DT properties.

Control flow: each setup function obtains parent names/counts, parent syscon/regmap, optional `clock-output-names`, ranges/divisors/IDs, registers the corresponding `clk_hw`, and publishes it with `of_clk_add_hw_provider()`. Multi-child nodes iterate children and register one provider per child. Conditional blocks compile optional domains based on `CONFIG_HAVE_AT91_*`.

State and persistence: per-node setup allocates characteristics/range arrays for clocks that need them; registered providers own their runtime state. There is no central `pmc_data` array in this legacy path; each node is a simple provider.

Dependencies and integration: bridges old DT bindings to helpers in `pmc.h`. It relies on syscon parent nodes, child `reg` properties, Atmel range/divisor properties, and compatibility-specific constants such as generated audio parent index 5.

Risks: some error paths leak allocated characteristics when regmap lookup fails after allocation; `clock-output-names` is read from parent nodes in child loops, which may not match per-child naming expectations; invalid child IDs are skipped silently. Test signals include booting old DTBs, every legacy compatible producing a clock provider, optional feature configs gating expected bindings, and range/divisor parsing behavior.
