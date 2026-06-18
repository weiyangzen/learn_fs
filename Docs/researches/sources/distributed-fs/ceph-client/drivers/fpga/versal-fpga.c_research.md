<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c

## Purpose
`versal-fpga.c` is the FPGA manager driver for Xilinx Versal devices. It delegates bitstream loading to the Xilinx firmware interface after setting the correct DMA addressing capability.

## Important APIs, types, and functions
The manager callbacks are `versal_fpga_ops_write_init()` and `versal_fpga_ops_write()` in `versal_fpga_ops`. Probe uses `dma_set_mask_and_coherent(..., DMA_BIT_MASK(44))` and `devm_fpga_mgr_register()`. The write path calls the Xilinx firmware FPGA load API with flags derived from `fpga_image_info`.

## Control flow
During probe, the platform device must support a 44-bit coherent DMA mask; otherwise the driver aborts. The write-init callback validates or records image flags without maintaining private state. The write callback passes the provided buffer and any partial-reconfiguration indication to platform firmware, which performs the actual programming operation.

## State and persistence behavior
This driver has essentially no private runtime state; registration is devm-managed and programming state is held by firmware and the FPGA manager core. There is no persistent state in the driver.

## Dependencies and integration points
It depends on the platform bus, OF match `xlnx,versal-fpga`, DMA mask setup, the FPGA manager framework, and Xilinx firmware services. It integrates with secure/platform firmware rather than programming PCAP registers directly.

## Risks and edge cases
The main risks are firmware-call failures, unsupported DMA masks, incorrect flag translation for partial reconfiguration, and lack of a state/status callback. Since the driver does not copy or DMA-map the buffer itself, buffer lifetime and firmware API expectations are critical integration assumptions.

## Test signals
Probe should fail cleanly without a 44-bit DMA-capable setup and register an FPGA manager when firmware is available. Programming tests should cover full and partial bitstreams, firmware failure returns, and device-tree matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/versal-fpga.c -->
