# sources/distributed-fs/ceph-client/drivers/reset/reset-sky1.c

Purpose: CIX Sky1 system reset controller, mapping numerous binding reset IDs to syscon/regmap offset-bit pairs for main S5 system-control and FCH reset blocks.

Important APIs/types/functions: `sky1_src_signal` maps offset and bit; `sky1_src_variant` selects signal arrays. `sky1_reset_set()` writes active-low reset bits through `regmap_update_bits()`. `sky1_reset_assert()`, `deassert()`, `reset()`, and `status()` implement reset ops with short sleeps. `sky1_reset_probe()` obtains the syscon regmap with `device_node_to_regmap()`.

Control flow: OF match data selects either `variant_sky1` or `variant_sky1_fch`. Probe registers `nr_resets` from the selected array. Runtime assert clears the bit, deassert sets it, and status reports asserted when the bit is clear.

State and persistence: signal tables are static; regmap bits hold hardware state. No runtime persistence beyond registered controller data.

Dependencies and integration: depends on CIX dt-bindings, syscon/regmap, OF platform probing, and reset-controller consumers.

Risks and test signals: several ops ignore return values from helper/regmap reads, so bus errors can look successful. Binding-array holes would make out-of-range or sparse IDs hazardous. Test both compatibles, active-low polarity, reset pulse delay, regmap failure injection, and DT binding ID coverage.
