# sources/distributed-fs/ceph-client/drivers/pinctrl/qcom/pinctrl-lpass-lpi.h

Purpose: public local header for LPASS LPI pinctrl variant drivers and the shared `pinctrl-lpass-lpi.c` implementation. It defines register offsets, masks, encoding helpers, table-construction macros, variant flags, data structures, and exported probe/remove prototypes.

Important APIs, types, and macros: register constants describe LPASS TLMM and slew registers: `LPI_GPIO_CFG_REG`, `LPI_GPIO_VALUE_REG`, pull/function/drive/OE/value masks, `LPI_SLEW_RATE_CTL_REG`, `LPI_SLEW_RATE_MASK`, and `LPI_TLMM_REG_OFFSET`. Bias constants encode disable, pull-down, keeper, and pull-up. `LPI_GPIO_DS_TO_VAL(v)` converts mA drive strength to hardware field value. `LPI_FUNCTION(fname)` creates `struct lpi_function` entries indexed by `LPI_MUX_*`. `LPI_PINGROUP()` and `LPI_PINGROUP_OFFSET()` create `struct lpi_pingroup` entries with GPIO plus four alternate muxes, optional slew offset, and optional predefined pin offset. `LPI_FLAG_SLEW_RATE_SAME_REG` and `LPI_FLAG_USE_PREDEFINED_PIN_OFFSET` control implementation behavior.

Control flow: the header itself has no runtime flow. Variant drivers include it to build static `pins`, `groups`, and `functions` arrays, fill `struct lpi_pinctrl_variant_data`, and call `lpi_pinctrl_probe()`/`lpi_pinctrl_remove()` from their platform driver callbacks.

State and persistence: no mutable state. The structures define immutable variant data consumed by the runtime implementation. Register constants define how persistent hardware state is encoded.

Dependencies and integration: includes `<linux/array_size.h>`, `<linux/bits.h>`, and `../core.h`, and forward-declares `platform_device` and `pinctrl_pin_desc`. It is tightly coupled to `pinctrl-lpass-lpi.c` and to LPASS variant files that define `LPI_MUX_*` enums and group arrays matching these macros.

Risks: macro-generated arrays rely on enum names and group arrays being present and correctly ordered. `LPI_PINGROUP()` fixes `.nfuncs = 5`; variants needing more mux options require a header change. `LPI_GPIO_DS_TO_VAL(v)` has no local validation and assumes implementation-side constraints. Flag misuse can make register offsets wrong or make the implementation require a missing slew resource.

Test signals: compile coverage from all LPASS LPI variant drivers; sparse/build warnings for pointer types; probe tests for variants with same-register slew and separate slew resources; pinconf read/write tests validating masks and drive/slew encodings; mux tests confirming `LPI_FUNCTION()` indices match `LPI_MUX_*` enum values.
