<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c

### Purpose
`clk-scmi.c` maps ARM SCMI clock protocol objects into CCF clocks. It dynamically selects operation sets per firmware-reported clock capabilities, including state, rate, parent, atomic transport, and optional OEM duty-cycle configuration.

### Important APIs, Types, And Functions
`struct scmi_clk` stores SCMI ID, device, `clk_hw`, firmware `scmi_clock_info`, protocol handle, and parent data. Key functions are `scmi_clk_recalc_rate()`, `scmi_clk_determine_rate()`, `scmi_clk_set_rate()`, parent get/set helpers, atomic and non-atomic enable/disable helpers, duty-cycle get/set helpers, `scmi_clk_ops_alloc()`, `scmi_clk_ops_select()`, `scmi_clk_ops_init()`, and `scmi_clocks_probe()`.

### Control Flow, State, And Persistence
Probe obtains the SCMI clock protocol, gets the firmware clock count, allocates onecell data and `struct scmi_clk` array, asks the transport whether atomic commands are supported, then iterates every clock. For each valid firmware clock, it chooses or reuses a `clk_ops` combination based on forbidden controls, enable latency, parent support, and duty-cycle probing, builds parent data from firmware parent IDs, registers the clock with `CLK_GET_RATE_NOCACHE`, and sets rate range from discrete list or linear range. State remains firmware-owned; the driver caches metadata and parent arrays.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the SCMI bus, clock protocol ops, OF onecell consumers, transport atomicity, firmware-provided parent topology, and optional OEM duty-cycle config. Risks include global `scmi_proto_clk_ops` shared across instances, parent indices referring to skipped or invalid clocks, duty-cycle integer truncation, unsupported firmware features only discovered at operation time, and per-instance devm `clk_ops` reuse constrained to probe stack database. Test signals include atomic and non-atomic transports, clocks with forbidden state/rate/parent controls, discrete and range rates, parent changes, duty-cycle get/set success and failure, invalid clock info holes, and suspend/resume firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-scmi.c -->
