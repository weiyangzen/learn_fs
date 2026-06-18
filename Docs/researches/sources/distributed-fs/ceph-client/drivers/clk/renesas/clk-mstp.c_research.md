# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-mstp.c

Purpose: This file implements legacy Renesas MSTP module-stop gate clocks and a companion always-on generic PM domain that attaches device clocks through PM clock helpers.

Important APIs, types, and functions: Core types are `mstp_clock_group` and `mstp_clock`. Key functions are `cpg_mstp_clock_endisable()`, `cpg_mstp_clock_register()`, `cpg_mstp_clocks_init()`, `cpg_mstp_attach_dev()`, `cpg_mstp_detach_dev()`, `cpg_mstp_add_clk_domain()`, and `cpg_mstp_pd_init_provider()`.

Control flow: `CLK_OF_DECLARE()` handles `renesas,cpg-mstp-clocks`, maps SMSTPCR and optional MSTPSR registers, parses output names and clock indices, registers per-bit gate clocks, and exposes a onecell provider. Enabling clears the module-stop bit and optionally polls MSTPSR until the module reports enabled.

State and persistence: Each group holds MMIO pointers, a spinlock, optional 8-bit mode, onecell data, and clock pointers. Hardware SMSTPCR/MSTPSR registers hold module-stop state. PM domain globals temporarily store the DT node and genpd until `postcore_initcall()` publishes the provider.

Dependencies and integration: Depends on CCF, OF, IO polling, PM clock, PM domain, and `linux/clk/renesas.h` declarations used by legacy SoC CPG files. Devices get module clocks either directly or via the MSTP PM domain attach path.

Risks: Enable polling timeout is only 10 microseconds, so slow hardware or wrong status wiring fails. `intc-sys` is marked critical by name. 8-bit support is special-cased for RZ/A1. PM-domain globals allow one pending provider.

Test signals: Boot legacy Renesas SoCs with MSTP DT nodes, enable/disable module clocks, validate MSTPSR polling, check PM domain attach adds the first MSTP clock to devices, and confirm `intc-sys` is never disabled.
