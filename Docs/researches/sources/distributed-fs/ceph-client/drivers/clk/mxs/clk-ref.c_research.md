# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk-ref.c

Purpose: Implements MXS PLL reference clocks. Four reference clocks share one register, each with an 8-bit lane containing a gate bit and a 6-bit fractional divisor.

Important APIs, types, and functions: `struct clk_ref` stores `clk_hw`, register, and lane index. `mxs_clk_ref()` registers the clock. `clk_ref_enable()` and `clk_ref_disable()` clear/set the lane gate bit. `clk_ref_recalc_rate()` computes `parent * 18 / FRAC`. `clk_ref_determine_rate()` and `clk_ref_set_rate()` clamp FRAC to 18..35 and update the lane under `mxs_lock`.

Control flow: SoC init creates references such as `ref_cpu`, `ref_emi`, `ref_pix`, and `ref_io`. Consumers request rates; the driver picks the closest valid FRAC and writes it to the lane.

State and persistence: Each `struct clk_ref` persists after registration. The divisor and gate state live in MMIO. Register updates are serialized with the shared MXS spinlock.

Dependencies and integration points: Used by both i.MX23 and i.MX28 topology files as parents for CPU, EMI, PIX, IO, HSADC, and GPMI paths. Depends on lane layout and CCF gate/rate ops.

Risks: A zero FRAC value in hardware would cause divide-by-zero in `recalc_rate()`. The implementation relies on init code programming sane fractional values. Clamping means requested rates outside the supported range silently become edge rates.

Test signals: Validate each reference lane rate follows `pll * 18 / frac`, gate bits clear/set on enable/disable, and set-rate clamps to FRAC 18 or 35 for out-of-range requests. Boot defaults should avoid zero FRAC fields.
