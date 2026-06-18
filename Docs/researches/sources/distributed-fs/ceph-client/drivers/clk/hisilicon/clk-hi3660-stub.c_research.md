# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660-stub.c

Purpose: implements Hi3660 firmware-mediated stub clocks for CPU clusters, GPU, and DDR using mailbox commands to LPM3 firmware and shared SRAM rate readback.

Important APIs/types/functions: `hi3660_stub_clk_chan` stores mailbox client/channel. `hi3660_stub_clk` stores ID, `clk_hw`, firmware command, message buffer, and cached rate. `DEFINE_CLK_STUB()` builds four clocks with `CLK_GET_RATE_NOCACHE`. Ops are `hi3660_stub_clk_recalc_rate()`, `hi3660_stub_clk_determine_rate()`, and `hi3660_stub_clk_set_rate()`.

Control flow: probe configures a nonblocking mailbox client, requests channel 0, maps the SRAM/resource region, offsets to `HI3660_STUB_CLOCK_DATA`, registers all stub `clk_hw`s, and publishes an OF provider that validates index arguments. Set-rate sends command plus MHz rate through mailbox and immediately marks tx done.

State and persistence: firmware owns the real clock programming. The driver reads rates from shared SRAM and stores a transient cached rate per stub clock. Global `freq_reg` and `stub_clk_chan` are singleton state.

Dependencies and integration points: depends on mailbox framework, DT binding IDs, `hisilicon,hi3660-stub-clk` compatible, and LPM3 firmware protocol command values.

Risks: mailbox send return value is ignored, so failed firmware requests appear successful. Probe leaks the mailbox channel on later failures because no remove/free path is defined. `devm_ioremap()` is used instead of resource-requesting helpers. Global singleton state makes multiple instances unsafe.

Test signals: verify mailbox traffic for each command, shared SRAM rate updates after set-rate, invalid phandle index handling, probe deferral/failure behavior when mailbox is absent, and CPU/GPU/DDR DVFS integration under load.
