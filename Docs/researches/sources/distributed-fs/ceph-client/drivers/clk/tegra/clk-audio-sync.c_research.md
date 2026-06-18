# sources/distributed-fs/ceph-client/drivers/clk/tegra/clk-audio-sync.c

Implements a simple software-controlled Tegra audio sync source clock. It has no hardware register; it stores the selected rate in memory and enforces a maximum.

`tegra_clk_sync_source_ops` implements `determine_rate`, `set_rate`, and `recalc_rate`. `determine_rate` rejects requests above `sync->max_rate`; `set_rate` stores `sync->rate`; `recalc_rate` returns that stored value. `tegra_clk_register_sync_source()` allocates `struct tegra_clk_sync_source`, fills `clk_init_data`, and calls `clk_register()`.

State is in the allocated clock object: `rate` and `max_rate`. It persists until the clock is unregistered, with no hardware side effects. The code depends on CCF registration and `struct tegra_clk_sync_source` declarations from `clk.h`. It is used by Tegra audio clock setup code as a programmable sync source.

Because rate is memory-only, suspend/resume has no hardware context to restore. Consumers must not expect parent propagation or hardware validation. Test signals include `clk_set_rate()` rejecting over-max requests and audio path clock summaries reflecting the stored rate.
