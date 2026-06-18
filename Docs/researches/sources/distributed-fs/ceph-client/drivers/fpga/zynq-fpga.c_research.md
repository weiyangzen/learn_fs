<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c

## Purpose
`zynq-fpga.c` is the FPGA manager driver for Xilinx Zynq-7000 PCAP/devcfg. It programs the programmable logic via DMA to PCAP, manages SLCR reset/level-shifter sequencing, handles encrypted and partial bitstream flags, and uses interrupts/completions to feed the PCAP DMA queue.

## Important APIs, types, and functions
`struct zynq_fpga_priv` stores IRQ, clock, devcfg MMIO base, SLCR regmap, DMA queue state, spinlock, current SG pointer, and completion. Manager callbacks are `zynq_fpga_ops_write_init()`, `zynq_fpga_ops_write()` as `.write_sg`, `zynq_fpga_ops_write_complete()`, and `zynq_fpga_ops_state()`. Key helpers include `zynq_step_dma()`, `zynq_fpga_isr()`, `zynq_fpga_has_sync()`, `zynq_fpga_set_irq()`, and MMIO read/write wrappers.

## Control flow
Probe maps devcfg registers, resolves the `syscon` SLCR regmap, gets IRQ and `ref_clk`, unlocks devcfg, clears/masks interrupts, requests the IRQ, and registers the FPGA manager. Write-init enables the clock, validates encrypted bitstreams against secure-boot state, validates full bitstreams for the byte-swapped Xilinx sync word, asserts PL resets and level shifters for full reconfiguration, toggles `PCFG_PROG_B`, enables PCAP/PR control, checks the DMA queue is empty, and disables PCAP loopback. The write path validates SG alignment, DMA maps the table, enables the clock, clears interrupts, seeds DMA state under `dma_lock`, calls `zynq_step_dma()`, waits up to five seconds for completion, disables IRQs, checks error and done bits, unmaps DMA, and reports detailed register state on failure. Completion polls for `IXR_PCFG_DONE_MASK`, releases PR control back to ICAP, and restores level shifters/resets for full reconfiguration.

## State and persistence behavior
Runtime state is in `zynq_fpga_priv`, hardware registers, the DMA-mapped scatterlist, and one completion object. `dma_lock`, `dma_elm`, `dma_nelms`, and `cur_sg` coordinate the handoff between process context and interrupt context. No state persists across unload; reset and level-shifter changes are hardware-visible side effects.

## Dependencies and integration points
The driver depends on platform/OF resources, clocks, IRQs, DMA mapping, scatterlists, completions, spinlocks, MMIO polling, SLCR syscon regmap, PM headers, and FPGA manager APIs. It integrates with the generic FPGA manager by accepting SG images and exposing manager state from PCAP done status.

## Risks and edge cases
Critical risks are DMA queue race handling, inability to cancel a failed DMA, SG alignment restrictions, timeout/error bit interpretation, encrypted-bitstream secure-mode enforcement, and full-vs-partial reset/level-shifter behavior. The expression checking DMA queue empty is precedence-sensitive but intended to require queue-not-full and queue-empty. Hardware errata around PCAP loopback, level shifters, and sync-word byte order are central to correct operation.

## Test signals
Signals include probe with valid devcfg/syscon/IRQ/clock, full bitstream sync-word rejection, encrypted bitstream rejection when not secure, SG alignment failures, DMA completion interrupt path, timeout/error register diagnostics, partial reconfiguration without global PL reset, and final `FPGA_MGR_STATE_OPERATING` when PCFG_DONE is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/zynq-fpga.c -->
