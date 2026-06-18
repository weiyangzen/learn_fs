# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona-setup.c

## Purpose
Validates and registers Broadcom Kona CCU clock data. It checks CCU and peripheral-clock descriptors for sane register ranges, bit positions, divider math, parent selector mappings, and trigger requirements before adding clocks and the OF onecell provider.

## Important APIs, Types, And Functions
The exported entry is `kona_dt_ccu_setup`. Validation helpers include `ccu_data_offsets_valid`, `peri_clk_data_offsets_valid`, `bit_posn_valid`, `bitfield_valid`, `policy_valid`, `gate_valid`, `hyst_valid`, `sel_valid`, `div_valid`, `kona_dividers_valid`, `trig_valid`, `peri_clk_data_valid`, and `kona_clk_valid`. Registration and cleanup helpers include `parent_process`, `clk_sel_setup`, `kona_clk_setup`, `kona_clk_teardown`, `ccu_clks_teardown`, `kona_ccu_teardown`, and `of_clk_kona_onecell_get`.

## Control Flow
`kona_dt_ccu_setup` converts the DT resource to a bounded register range, validates CCU-wide data, maps the CCU registers, records the node, then loops over predefined `kona_clks` and registers each populated clock. Parent processing compacts parent-name arrays by dropping `BAD_CLK_NAME` placeholders and creates a selector-value map that preserves original hardware selector positions. After adding the provider, `kona_ccu_init` programs initial hardware state.

## State And Persistence
Setup fills mutable fields in clock descriptors: allocated parent name arrays, selector value arrays, `clk_hw.init`, CCU base address, node reference, range, and provider state. Teardown frees selector arrays, unregisters clocks, deletes the provider, drops the node, and unmaps MMIO.

## Dependencies And Integration Points
Depends on `clk-kona.h` descriptor macros, OF address translation, common clock registration, and the runtime initializer in `clk-kona.c`. SoC-specific CCU definitions call this function from their `CLK_OF_DECLARE` paths.

## Risks And Edge Cases
The registration loop ignores individual `kona_clk_setup` return values and relies on later error checks imperfectly, so malformed individual clocks can leave partial providers. Parent arrays use dynamically allocated copies that must be freed on failures. Missing triggers are fatal when selectors or variable dividers require hardware commit. Fractional pre-divider plus divider widths must not overflow scaled arithmetic.

## Test Signals
Exercise invalid offsets outside the DT resource, bit positions above 31, zero-width selectors, unsupported parent placeholders, multiple parents without selectors, pre-trigger without trigger, variable divider without trigger, provider lookup bounds, and teardown after mid-registration failures.
