<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c

Purpose: This platform driver exposes the BCM2711 DVP controller's two HDMI 108 MHz gated clocks and six reset lines.

Important APIs, types, and functions: `clk_dvp` stores a onecell clock array and `reset_simple_data`. `clk_dvp_probe()` maps the controller registers, registers a reset controller with `reset_simple_ops`, registers two gate clocks (`hdmi0-108MHz`, `hdmi1-108MHz`) using `clk_hw_register_gate_parent_data()`, and publishes an OF clock provider. `clk_dvp_remove()` unregisters the gate clocks.

Control flow: Probe allocates state, maps MMIO, sets the reset controller base at `DVP_HT_RPI_SW_INIT`, registers the reset controller, creates the two gate clocks backed by `DVP_HT_RPI_MISC_CONFIG` bits 3 and 4 with `CLK_GATE_SET_TO_DISABLE`, and adds the onecell provider. Failure after clock registration unwinds the created gates.

State and persistence behavior: The gate and reset state lives in DVP MMIO registers. A single spinlock in `reset_simple_data` protects both reset and gate register access. Driver allocations are devm-managed except explicit gate unregisters.

Dependencies and integration points: It depends on the reset controller framework, common clock framework, one parent clock from DT index 0, and compatible `"brcm,brcm2711-dvp"`. Consumers are HDMI/DVP-related drivers needing clock and reset control.

Risks and test signals: Risks include shared lock assumptions, gate polarity (`SET_TO_DISABLE`), missing provider cleanup in remove, and reset count/index mismatch. Tests should verify HDMI clock enables, reset assertion/deassertion, provider indices, and module unload/reprobe if built modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-bcm2711-dvp.c -->
