<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c

## Purpose
`zynqmp-fpga.c` is the FPGA manager driver for Xilinx ZynqMP PCAP. It copies bitstreams into coherent DMA memory and asks ZynqMP platform firmware to load them, exposing a sysfs status attribute for firmware configuration status.

## Important APIs, types, and functions
`struct zynqmp_fpga_priv` stores the device pointer and current FPGA manager flags. Manager callbacks are `zynqmp_fpga_ops_write_init()`, `zynqmp_fpga_ops_write()`, and `zynqmp_fpga_ops_state()`. `status_show()` exports `zynqmp_pm_fpga_get_config_status()`. Firmware calls include `zynqmp_pm_fpga_load()` and `zynqmp_pm_fpga_get_status()`.

## Control flow
Probe allocates private data and registers an FPGA manager named `Xilinx ZynqMP FPGA Manager`, with device attribute group `status`. Write-init records image flags. Write allocates a coherent DMA buffer, copies the bitstream, issues a write memory barrier, sets the partial flag if requested, calls firmware to load the FPGA, then frees the buffer. State reads firmware status and reports operating when `IXR_FPGA_DONE_MASK` is set.

## State and persistence behavior
The private `flags` field persists only between write-init and write for one load operation. Coherent DMA memory is allocated per write and freed immediately after the firmware call. Long-lived state is in platform firmware and FPGA hardware, not in the driver.

## Dependencies and integration points
It depends on coherent DMA APIs, FPGA manager, platform/OF matching `xlnx,zynqmp-pcap-fpga`, and the Xilinx ZynqMP firmware interface. The sysfs `status` file integrates firmware configuration status into the manager device.

## Risks and edge cases
Large bitstreams require a contiguous coherent allocation, which can fail under memory pressure. Firmware failures are returned directly. The driver stores flags in shared manager private data, so callers rely on manager serialization. State reporting ignores errors from `zynqmp_pm_fpga_get_status()`.

## Test signals
Probe, full and partial firmware loads, coherent allocation failure injection, firmware error propagation, sysfs `status` reads, and operating/unknown state transitions from firmware status are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynqmp-fpga.c -->
