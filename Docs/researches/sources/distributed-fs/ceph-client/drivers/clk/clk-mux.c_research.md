# sources/distributed-fs/ceph-client/drivers/clk/clk-mux.c

Purpose: generic common-clock mux implementation for clocks that select one parent from a register field. It also provides registration/unregistration helpers and conversion helpers for table/index encodings.

Important APIs, types, and functions: `clk_mux_val_to_index()` maps raw hardware values to parent indexes using optional tables, one-based indexes, or bit indexes. `clk_mux_index_to_val()` performs the inverse. `clk_mux_ops` supports get/set parent and rate determination; `clk_mux_ro_ops` supports read-only muxes. `__clk_hw_register_mux()`, `__devm_clk_hw_register_mux()`, `clk_register_mux_table()`, `clk_unregister_mux()`, and `clk_hw_unregister_mux()` are exported.

Control flow: get-parent reads, shifts, masks, and converts the register value. set-parent converts the requested index, locks if provided, either writes a hiword mask or performs RMW, then writes the new value. Registration validates hiword width, allocates `struct clk_mux`, fills `clk_init_data` with parent names/hws/data, selects writable or read-only ops, and registers with device or OF context.

State and persistence: hardware state is the mux register field. Software state is allocated mux metadata and optional table. Hiword mode avoids preserving unrelated fields through RMW. Optional locks protect shared registers.

Dependencies and integration points: core common-clock helper used by many platform drivers. Depends on MMIO accessors, endian flags, OF/device registration, devres, and clock rate helper `clk_mux_determine_rate_flags()`.

Risks and test signals: invalid hardware values return `-EINVAL` from a function typed as `u8` in get-parent paths, which can become an out-of-range parent index. Caller-provided masks/tables must match parent count. Test signals include table and index modes, hiword validation, read-only mux behavior, endian access, and devm unregister.
