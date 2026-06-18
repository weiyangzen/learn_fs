<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c

## Purpose
`xilinx-core.c` provides shared FPGA manager logic for Xilinx Spartan-6 and 7 Series slave-serial/selectmap-style configuration drivers. Transport drivers supply a byte-write callback while this core handles PROGRAM_B, INIT_B, DONE GPIO sequencing, manager state, full-bitstream validation policy, and post-write completion polling.

## Important APIs, types, and functions
The exported integration point is `xilinx_core_probe()`. Internal manager callbacks are `xilinx_core_state()`, `xilinx_core_write_init()`, `xilinx_core_write()`, and `xilinx_core_write_complete()`. `wait_for_init_b()` handles INIT_B polling or fallback delays, `get_done_gpio()` reads DONE, and `xilinx_core_devm_gpiod_get()` supports modern and legacy GPIO names for old slave-serial bindings.

## Control flow
Transport probes fill `struct xilinx_fpga_core` with `dev` and `write`, then call `xilinx_core_probe()`. Probe acquires PROGRAM_B, optional INIT_B legacy-compatible names, DONE, and registers an FPGA manager. Programming rejects `FPGA_MGR_PARTIAL_RECONFIG`, asserts PROGRAM_B low through the active-low GPIO abstraction, waits for INIT_B assert/deassert, verifies DONE is low, then waits program latency. The write callback delegates all bytes to the transport. Completion repeatedly writes `0xff` padding to supply extra CCLK cycles while polling DONE until `config_complete_timeout_us` expires, then reports INIT_B-derived diagnostic messages on timeout.

## State and persistence behavior
The core stores GPIO descriptors in the transport-owned `struct xilinx_fpga_core`. No file or firmware state is persisted. Hardware state is represented only through GPIO levels and the FPGA manager state callback, which reports reset when DONE is low and unknown otherwise.

## Dependencies and integration points
It depends on GPIO descriptors, OF compatibility checks for legacy names, delay/jiffies helpers, and the FPGA manager framework. It integrates with `xilinx-spi.c` and `xilinx-selectmap.c` through the `write` transport callback and exports `xilinx_core_probe()` as GPL.

## Risks and edge cases
Partial reconfiguration is explicitly unsupported. INIT_B may be absent, causing fixed fallback delays instead of positive hardware confirmation. Completion relies on the transport accepting one-byte padding writes, and diagnostics differ depending on INIT_B availability. GPIO polarity must be described correctly in firmware tables or reset sequencing will invert.

## Test signals
Signals include successful probe by both SPI and SelectMAP transports, rejection of partial reconfiguration, INIT_B timeout handling, DONE polling success after padding clocks, transport write failure propagation, and legacy `prog_b`/`init-b` GPIO-name compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/xilinx-core.c -->
