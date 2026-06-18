# sources/distributed-fs/ceph-client/drivers/clk/clk-fsl-flexspi.c


### Purpose
`clk-fsl-flexspi.c` provides a divider-table clock for Layerscape FlexSPI controllers. It exposes the FlexSPI clock divider register as a CCF clock provider for LS1028A and LX2160A variants.

### Important APIs, Types, And Functions
Variant tables `ls1028a_flexspi_divs` and `lx2160a_flexspi_divs` map hardware field values to supported dividers. The only probe path is `fsl_flexspi_clk_probe()`, which registers a `devm_clk_hw_register_divider_table()` clock and `devm_of_clk_add_hw_provider()`.

### Control Flow, State, And Persistence
Probe obtains the variant table from OF match data, maps the first resource with `devm_ioremap()` rather than claiming it, obtains parent clock name from DT index 0, applies optional `clock-output-names`, registers a 5-bit divider at shift 0, and installs a simple provider. Persistent state is the hardware divider field and the devm-managed clock registration.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include platform resources that may be shared with a parent device, OF parent clock, divider-table CCF helper, and compatible strings `fsl,ls1028a-flexspi-clk` and `fsl,lx2160a-flexspi-clk`. Risks include shared MMIO lifetime with parent devices, no explicit spinlock for shared register protection, parent-clock absence, and table differences where LS1028A accepts divider 1 but LX2160A starts at divider 2. Test signals include probe on both compatibles, divider table round/set behavior, shared-resource mapping, provider lookup by FlexSPI consumers, and failure paths for missing resource/parent/table.
