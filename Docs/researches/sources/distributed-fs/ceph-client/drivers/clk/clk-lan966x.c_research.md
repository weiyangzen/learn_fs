# sources/distributed-fs/ceph-client/drivers/clk/clk-lan966x.c

Purpose: Microchip LAN966x/LAN969x generic clock controller driver. It registers per-peripheral generic clocks with parent mux and prescaler controls, and optional additional simple gate clocks from a second MMIO resource.

Important APIs, types, and functions: `lan966x_gck` stores one generic clock register. `lan966x_gck_ops` implements enable/disable, set/recalc/determine rate, and get/set parent. `clk_gate_soc_desc` describes optional gate clocks. `lan966x_match_data` selects SoC-specific names, counts, and gate descriptors.

Control flow: probe reads match data, allocates `clk_hw_onecell_data`, maps resource 0 as the generic clock base, sets shared init ops, registers each generic clock at `base + i * 4`, then optionally maps resource 1 and registers SoC gate clocks. Finally it exposes the onecell provider with either generic-only or total clock count.

State and persistence: hardware state is per-clock `GCK_ENA`, `GCK_SRC_SEL`, and `GCK_PRESCALER` fields plus optional gate bits. Software state is devm-managed. A file-scope `base` is used during registration.

Dependencies and integration points: depends on platform resources, OF match data, common clock onecell provider, `FIELD_GET/PREP`, and generic gate helpers with a shared spinlock.

Risks and test signals: `lan966x_gck_set_rate()` does not validate divider overflow or exact divisibility; a zero divider can underflow if requested rate exceeds parent rate. `hw_data->num` changes only when resource 1 exists, so DT IDs differ by available resource. The global `base` is not per-device safe if multiple instances were ever probed. Test signals are DT binding coverage for both SoCs, parent selection, prescaler programming, and optional gate resource presence.
