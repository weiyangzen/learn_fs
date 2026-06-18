<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h

## Purpose
`xilinx-core.h` is the private shared interface between Xilinx transport-specific FPGA manager drivers and the common Xilinx configuration core.

## Important APIs, types, and functions
It defines `struct xilinx_fpga_core`, whose public fields are `struct device *dev` and `int (*write)(...)`. Private fields `prog_b`, `init_b`, and `done` are populated by `xilinx-core.c`. The sole function prototype is `xilinx_core_probe()`.

## Control flow
Transport drivers allocate or embed `struct xilinx_fpga_core`, initialize `dev` and `write`, then call `xilinx_core_probe()`. After that, FPGA manager callbacks in the core use the transport `write` operation for data and padding clocks.

## State and persistence behavior
The structure carries runtime-only pointers and GPIO descriptors. The header defines no persistent format and no executable logic.

## Dependencies and integration points
It depends on `linux/device.h`; the GPIO type is forward-used via pointers populated in the C file. It integrates `xilinx-spi.c`, `xilinx-selectmap.c`, and `xilinx-core.c`.

## Risks and edge cases
The comment separates public and private fields, but C cannot enforce that boundary. Transport drivers must keep the structure alive for the manager lifetime and must provide a valid `write` callback before probe.

## Test signals
Build coverage of both transports, successful manager probe, and write callback invocation through firmware loads validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.h -->
