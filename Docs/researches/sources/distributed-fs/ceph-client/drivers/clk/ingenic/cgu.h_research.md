# sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h -->
## sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h

### Purpose
`cgu.h` defines the declarative data model and public API used by Ingenic CGU SoC drivers. It describes PLL register layouts, mux fields, divider fields, fixed dividers, gate bits, custom ops, CGU instances, and private clock wrappers.

### Important APIs, Types, And Functions
Key types are `struct ingenic_cgu_pll_info`, `ingenic_cgu_mux_info`, `ingenic_cgu_div_info`, `ingenic_cgu_fixdiv_info`, `ingenic_cgu_gate_info`, `ingenic_cgu_custom_info`, `ingenic_cgu_clk_info`, `ingenic_cgu`, and `ingenic_clk`. The `CGU_CLK_*` bit flags describe clock capabilities. Public functions are `ingenic_cgu_new()` and `ingenic_cgu_register_clocks()`, and `to_ingenic_clk()` maps `clk_hw` to driver state.

### Control Flow, State, And Persistence
The header has no runtime control flow, but it defines how runtime code interprets state: clock tables index parents through the same array, PLLs can have custom M/N/OD calculators and set-rate hooks, dividers may require change-enable or busy polling, and gates can use inverted polarity plus stabilization delays. SoC files persist their clock topology in static arrays of this structure.

### Dependencies, Integration Points, Risks, And Test Signals
The header integrates common clock callbacks with OF onecell providers and SoC-specific DT binding IDs. Risks include field-order mistakes in positional initializers, unsupported combinations of `CGU_CLK_*` bits, parent index drift from dt-bindings, and custom clock ops bypassing generic protections. Test signals are compile warnings for initializer mismatches, provider registration of all table entries, rate/parent operations across mux/div/gate combinations, and ABI consistency with DT binding clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/ingenic/cgu.h -->
