# sources/distributed-fs/ceph-client/drivers/clk/mxs/clk.h

Purpose: Declares the shared MXS clock helper API and small inline wrappers around common CCF clock types.

Important APIs, types, and functions: Exposes `mxs_lock`, `mxs_clk_wait()`, `mxs_clk_pll()`, `mxs_clk_ref()`, `mxs_clk_div()`, and `mxs_clk_frac()`. Inline helpers register fixed-rate, gate, mux, and fixed-factor clocks. Defines MXS SET/CLR register offsets.

Control flow: SoC topology files include this header and compose clock trees by calling helper constructors. Inline gate and mux helpers consistently apply `CLK_SET_RATE_PARENT`; muxes also use `CLK_SET_RATE_NO_REPARENT`.

State and persistence: The header declares shared state but owns none directly. Registered clocks and MMIO state persist through the implementation files.

Dependencies and integration points: Depends on Linux CCF and spinlock definitions. It is the integration contract between generic MXS helper implementations and `clk-imx23.c`/`clk-imx28.c`.

Risks: Inline helpers bake in flags and lock choices for all SoC users. The gate helper uses `CLK_GATE_SET_TO_DISABLE`, so users must only pass gates with inverted set-to-disable semantics. The mux helper prevents reparenting during rate changes, which is correct for these trees but would surprise new users if reused elsewhere.

Test signals: Build tests should catch signature drift between declarations and implementations. Runtime checks should verify inline gate and mux semantics match hardware for every caller.
