# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-common.h

Purpose: this header defines the common embedding contract used by all OWL clock types and SoC descriptors.

Important types: `struct owl_clk_common` embeds a `struct clk_hw` plus the shared `struct regmap *`. Every concrete OWL clock type places this member at the end and uses `container_of` conversion helpers. `struct owl_clk_desc` groups the array of common clocks, `clk_hw_onecell_data`, reset map, reset count, and initialized regmap for a SoC.

Important APIs: `hw_to_owl_clk_common()` converts framework callbacks back to the common object. `owl_clk_regmap_init()` and `owl_clk_probe()` are exported within the local driver family.

Control flow/state: the header does not own state, but its layout enables callback dispatch from generic `clk_ops` into OWL-specific register descriptions. The descriptor couples clock and reset registration by sharing the same regmap.

Risks and tests: all concrete structures rely on the embedded `common` field and conversion helpers being correct. Type mismatch or non-OWL `clk_hw` use would corrupt callback state. Test signals are successful registration of each clock class, `container_of` coverage through enable/disable/rate changes, and sparse/compiler checking for forward declarations.
