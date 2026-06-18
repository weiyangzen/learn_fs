# sources/distributed-fs/ceph-client/drivers/clk/clk-axi-clkgen.c

## Purpose
Implements the Analog Devices AXI clkgen pcore clock generator. It programs Xilinx MMCM dynamic reconfiguration registers to synthesize requested output rates, supports parent selection, and adapts operating limits to FPGA family, speed grade, voltage, and pcore version.

## Important APIs, Types, And Functions
Types include `axi_clkgen_limits`, `axi_clkgen`, and `axi_clkgen_div_params`. Important helpers are `axi_clkgen_calc_params`, `axi_clkgen_calc_clk_params`, `axi_clkgen_wait_non_busy`, `axi_clkgen_mmcm_read`, `axi_clkgen_mmcm_write`, `axi_clkgen_mmcm_enable`, `axi_clkgen_set_div`, `axi_clkgen_set_rate`, `axi_clkgen_determine_rate`, `axi_clkgen_get_div`, `axi_clkgen_recalc_rate`, `axi_clkgen_setup_limits`, and `axi_clkgen_probe`.

## Control Flow
Probe maps registers, handles optional `s_axi_aclk`, validates parent count, reads parent names, selects default or discovered FPGA limits, names the output clock, disables the MMCM, registers the clock, and adds a simple OF provider. Rate determination searches integer and fractional MMCM divider combinations within PFD/VCO limits. Set-rate writes power, output divider, input divider, feedback divider, lock, and filter registers through the DRP interface.

## State And Persistence
The driver stores base, `clk_hw`, and selected limits. Hardware persists reset/MMCM enable, parent select, and DRP-programmed MMCM registers. It does not cache the programmed rate; recalc reads MMCM dividers back.

## Dependencies And Integration Points
Depends on ADI AXI version/info registers, Xilinx MMCM DRP semantics, CCF APIs, optional AXI bus clock, OF compatibles `adi,axi-clkgen-2.00.a` and `adi,zynqmp-axi-clkgen-2.00.a`, and module platform-driver binding.

## Risks And Edge Cases
DRP busy timeouts return `-EIO`; some write paths do not propagate read-modify-write failures. Parameter search uses kHz scaling and may lose precision. Parent count differs between legacy and named AXI-clock DTs. Unknown speed grades fail probe for newer pcores.

## Test Signals
Mock register tests for DRP busy handling, set/recalc consistency across integer and fractional rates, parent get/set, pcore-version limit selection, voltage-limited speed grade behavior, invalid parent counts, and zero parent/requested rates.
