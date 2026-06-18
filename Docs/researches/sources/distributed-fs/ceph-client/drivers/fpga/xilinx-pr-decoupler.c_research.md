<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c

## Purpose
`xilinx-pr-decoupler.c` is an FPGA bridge driver for Xilinx PR Decoupler and DFX AXI Shutdown Manager IP. It exposes coupling/decoupling of a reconfigurable region through the FPGA bridge framework.

## Important APIs, types, and functions
`struct xlnx_pr_decoupler_data` stores match-specific naming, MMIO base, and AXI clock. Bridge ops are `xlnx_pr_decoupler_enable_set()` and `xlnx_pr_decoupler_enable_show()`. Probe uses `device_get_match_data()`, `devm_platform_ioremap_resource()`, `devm_clk_get("aclk")`, and `fpga_bridge_register()`.

## Control flow
Probe maps the control register, obtains and prepares the AXI clock, verifies it can be enabled, disables it, then registers an FPGA bridge with the matched IP name. `enable_set(true)` enables the clock, writes zero to couple traffic, disables the clock, and returns. `enable_set(false)` writes bit 0 to decouple/shutdown. `enable_show()` reads the same register and returns logical enabled when the register is zero. Remove unregisters the bridge and unprepares the clock.

## State and persistence behavior
The driver stores only MMIO, clock, and IP config pointers. Bridge state is the hardware control register; no software persistence exists.

## Dependencies and integration points
It depends on platform devices, OF match data for `xlnx,pr-decoupler*` and `xlnx,dfx-axi-shutdown-manager*`, clock APIs, MMIO helpers, and the FPGA bridge framework. FPGA regions can use this bridge to isolate logic during partial reconfiguration.

## Risks and edge cases
Clock enable failures block both set and show operations. The driver assumes register value zero means coupled and any nonzero value means decoupled. It does not use runtime PM, does not serialize bridge ops beyond bridge core locking, and does not validate clock/reset state after register writes.

## Test signals
Probe/remove with each compatible string, bridge enable/disable operations, `enable_show()` matching register state, clock failure injection, and region programming flows that include this bridge are useful validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-pr-decoupler.c -->
