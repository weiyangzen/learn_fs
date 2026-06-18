<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c

## Purpose

`xlnx_vcu.c` initializes Xilinx VCU LogicoreIP isolation/reset and provides VCU clocks derived from a programmable VCU PLL.

## Important APIs, Types, And Functions

`struct xvcu_device` stores clocks, optional reset GPIO, logicore regmap, VCU SLCR base, PLL handles, and provider data. `struct vcu_pll` implements PLL CCF ops. `xvcu_pll_cfg[]` maps feedback dividers 25..125 to analog PLL settings. Helpers register the PLL, fixed post-divider, and four leaf clocks (`venc_core_clk`, `venc_mcu_clk`, `vdec_core_clk`, `vdec_mcu_clk`) each as mux/divider/gate chains.

## Control Flow

Probe maps `vcu_slcr`, locates `xlnx,vcu-settings` syscon or direct `logicore` resource, gets `aclk` and `pll_ref`, enables `aclk`, toggles optional reset GPIO, writes `VCU_GASKET_INIT`, registers the clock provider, and stores drvdata. Remove unregisters leaf clocks, asserts isolation/reset through GPIO and gasket register, and disables `aclk`.

## State And Persistence Behavior

PLL, leaf mux/divider/gate, gasket, and reset state persist in hardware. Runtime state is devm-managed except several manually registered leaf components that are explicitly unregistered. PLL enable waits up to two seconds for lock before clearing bypass.

## Dependencies And Integration Points

It depends on Xilinx VCU syscon definitions, regmap, GPIO descriptors, platform resources named `vcu_slcr` and optionally `logicore`, clocks `aclk` and `pll_ref`, and DT binding IDs from `xlnx-vcu.h`.

## Risks And Test Signals

Risks include post-divider requiring hardware value 1, exact PLL feedback table limits, optional reset GPIO warning path, manual unregister ordering, and lock timeout. Test VCU probe/remove, PLL set-rate/lock, encoder/decoder clock parent switching, gasket isolation, and both syscon and direct logicore paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/xlnx_vcu.c -->
