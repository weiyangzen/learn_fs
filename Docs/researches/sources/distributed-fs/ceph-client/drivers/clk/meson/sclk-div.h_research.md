# sources/distributed-fs/ceph-client/drivers/clk/meson/sclk-div.h

Purpose: This header declares the data contract for Meson sample-clock dividers implemented by `sclk-div.c`.

Important APIs, types, and functions: `struct meson_sclk_div_data` contains a divider `struct parm`, optional high-time `struct parm`, cached divider value, and cached `struct clk_duty`. It declares the exported `meson_sclk_div_ops` clock operations table.

Control flow: The header has no executable control flow. Clock definition files embed this data structure in `struct clk_regmap.data`; the ops implementation casts it back and uses the `parm` descriptors to access regmap fields.

State and persistence behavior: The cached fields are per-clock runtime state used by the implementation to preserve desired divider and duty cycle across hardware gating. The `parm` members are static register metadata and do not change.

Dependencies and integration points: It includes `linux/clk-provider.h` for duty-cycle and ops types and `parm.h` for Meson register-field descriptors. It is consumed by Meson SoC clock files that need sample/LR clock dividers.

Risks and edge cases: Callers must initialize `div.width` correctly because max divider calculation depends on it. `hi` may be non-applicable, so users must rely on `MESON_PARM_APPLICABLE` behavior in the C file. Test signals are primarily compile-time integration plus runtime duty-cycle/rate tests for clock definitions using this struct.
