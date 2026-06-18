<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c -->
## sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c

### Purpose
`clk-rpmi.c` is a RISC-V RPMI mailbox-backed clock provider. It discovers clocks from firmware, retrieves supported rate formats, and translates CCF rate and enable operations into RPMI clock service messages.

### Important APIs, Types, And Functions
Important types include `struct rpmi_clk_context`, `struct rpmi_clk`, `union rpmi_clk_rates`, and the packed TX/RX message structs for get attributes, supported rates, get/set rate, and set config. Major functions are `rpmi_clk_get_num_clocks()`, `rpmi_clk_get_attrs()`, `rpmi_clk_get_supported_rates()`, `rpmi_clk_recalc_rate()`, `rpmi_clk_determine_rate()`, `rpmi_clk_set_rate()`, `rpmi_clk_enable()`, `rpmi_clk_disable()`, `rpmi_clk_enumerate()`, and `rpmi_clk_probe()`.

### Control Flow, State, And Persistence
Probe configures a blocking mailbox client, requests channel 0, registers devm cleanup, validates RPMI message and clock service versions, obtains maximum message data size, asks firmware for clock count, enumerates every clock, and adds a onecell provider. Enumeration reads attributes, allocates rate storage, receives discrete or linear supported-rate data, registers a no-parent clock with `CLK_GET_RATE_NOCACHE`, and sets the allowed CCF rate range. Runtime operations send mailbox messages for get rate, set rate, enable, and disable; local state caches only metadata and supported ranges.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include RISC-V RPMI mailbox transport, `rpmi_mbox_*` helpers, `rpmi_to_linux_error()`, OF compatible `riscv,rpmi-clock`, and firmware correctness. Risks include `num_rates` exceeding the fixed 16-entry discrete array, subtle pagination bugs in supported-rate retrieval, returning negative errors through unsigned `recalc_rate`, ignoring disable message failures, and no parent or state query support. Test signals include version/service mismatch rejection, multi-message discrete rate enumeration, linear rate rounding, firmware error translation, CCF rate range enforcement, enable/disable message tracing, and all discovered clocks appearing in `clk_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/clk-rpmi.c -->
