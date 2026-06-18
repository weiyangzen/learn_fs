# sources/distributed-fs/ceph-client/drivers/dma/sun6i-dma.c

## Purpose
`sun6i-dma.c` is the DMAEngine provider for newer Allwinner DMA controllers starting with A31 and covering A23/A83T/H3/V3s/A64/A100/H6/D1-style variants. Unlike the sun4i driver, this hardware supports linked-list items, so SG and cyclic transfers are represented as DMA-pool allocated LLIs consumed by the controller.

## Important APIs, Types, and Functions
`struct sun6i_dma_config` holds variant-specific channel/request/vchan counts, clock-autogate callback, register field encoders for burst, DRQ and mode, supported burst lengths and address widths, and flags for high address and MBUS clock support. `struct sun6i_dma_dev` owns the DMAEngine device, MMIO, clocks, reset, IRQ, tasklet, pending vchan list, descriptor pool, physical channels, virtual channels, and variant config. `struct sun6i_dma_lli` is the hardware descriptor with a CPU-only `v_lli_next`. `struct sun6i_desc` wraps the first physical and virtual LLI pointers in a virt-dma descriptor. `struct sun6i_pchan` tracks current and completed descriptors for a hardware channel; `struct sun6i_vchan` tracks the virtual channel, slave config, pending-list node, port, IRQ type, assigned physical channel, and cyclic flag.

Key functions are `sun6i_dma_lli_add()`, `sun6i_dma_start_desc()`, `sun6i_dma_tasklet()`, `sun6i_dma_interrupt()`, `set_config()`, `sun6i_dma_prep_dma_memcpy()`, `sun6i_dma_prep_slave_sg()`, `sun6i_dma_prep_dma_cyclic()`, `sun6i_dma_tx_status()`, pause/resume/terminate functions, and `sun6i_dma_probe()`.

## Control Flow
Probe obtains variant data, maps registers, gets clocks and reset, creates the LLI DMA pool, initializes pending and channel structures, reads or derives channel/request/vchan counts, deasserts reset, enables clocks including optional MBUS, requests the IRQ, registers DMAEngine and OF DMA, and enables variant clock autogating if needed.

OF translation takes one cell, the DRQ port, validates it against `max_request`, allocates any slave channel, and stores the port. Preparation allocates one or more LLIs. Memcpy creates a single SDRAM-to-SDRAM LLI. Slave SG creates an LLI per SG entry with direction-dependent DRQ and linear/IO modes. Cyclic creates one LLI per period and links the last physical LLI back to the first.

`issue_pending()` adds the vchan to the controller pending list and schedules the tasklet. The tasklet first advances channels whose previous descriptor completed, then assigns free physical channels to pending vchans, and starts descriptors by programming interrupt type, LLI address, and channel enable. The IRQ handler reads/clears status registers, invokes cyclic callbacks on package interrupts, completes non-cyclic descriptors on queue interrupts, marks `pchan->done`, and schedules the tasklet to continue or free the channel.

## State and Persistence
State is in memory and MMIO only: LLI chains in the DMA pool, pending vchan list, pchan/vchan associations, active and done descriptors, cyclic flag, IRQ type, and tasklet shutdown flag. No file or disk state is written. Remove unregisters OF/DMAEngine, disables interrupts, kills tasklets, disables clocks, asserts reset, and removes channels from the DMAEngine list.

## Dependencies and Integration Points
The driver uses DMAEngine, virt-dma, OF DMA, platform devices, clocks, reset controls, DMA pools, tasklets, spinlocks, and Allwinner DT compatibles for A31, A23, A83T, H3, V3s, D1, A64, A100, and H6. It advertises private memcpy/slave/cyclic DMA with variant-specific address widths, burst support, and burst residue granularity. Newer variants can encode high address bits in LLI `para` and may require an MBUS clock.

## Risks and Edge Cases
`sun6i_dma_tx_status()` calls `to_sun6i_desc(&vd->tx)` before checking whether `vd` is non-null, so active-descriptor status paths must avoid null dereference assumptions. Cyclic descriptors deliberately form a physical ring; free paths walk the CPU `v_lli_next` chain, which remains non-cyclic, so preserving that invariant is important. High address handling only stores two upper bits. Pause of an unassigned vchan removes it from the pending list; resume re-adds it only when issued descriptors exist. Interrupt channel indexing shifts status by groups of eight and depends on `num_pchans` and status layout matching the hardware.

## Test Signals
Validate probe across variants with fixed and DT-derived channel counts, MBUS-clock variants, high-address transfers, memcpy, slave SG with multiple LLIs, cyclic period callbacks, pause/resume before and after pchan assignment, terminate of cyclic and non-cyclic transfers, residue for pending versus active descriptors, and tasklet shutdown during remove/error paths.
