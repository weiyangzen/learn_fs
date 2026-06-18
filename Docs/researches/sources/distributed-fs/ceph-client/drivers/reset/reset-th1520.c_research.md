# sources/distributed-fs/ceph-client/drivers/reset/reset-th1520.c

Purpose: T-HEAD TH1520 reset controller family driver covering top-level, AP, DSP, miscellaneous, VI, and VP reset blocks with per-compatible register maps.

Important APIs/types/functions: `th1520_reset_map` maps binding IDs to register offsets and bit masks; `th1520_reset_data` selects a table and count. `th1520_reset_assert()` clears the mapped bit and `th1520_reset_deassert()` sets it through regmap. Probe maps MMIO, initializes a 32-bit regmap, optionally asserts GPU resets for `thead,th1520-reset`, and registers reset ops.

Control flow: OF match data chooses one of six reset tables. Consumers assert/deassert by ID, which indexes directly into the selected table.

State and persistence: static tables encode hardware layout. Register bits persist in hardware; software only holds regmap, table pointer, and rcdev.

Dependencies and integration: platform MMIO, regmap, `dt-bindings/reset/thead,th1520-reset.h`, and reset-controller consumers.

Risks and test signals: direct sparse-array indexing can access zero-initialized table slots if binding IDs are non-contiguous or invalid but below `nr_resets`. There is no status op. Test every compatible, GPU initialization behavior, table/binding continuity, invalid IDs, and regmap update failures.
