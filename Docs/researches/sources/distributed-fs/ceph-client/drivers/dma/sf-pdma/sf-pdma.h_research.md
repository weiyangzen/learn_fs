# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/sf-pdma.h

Purpose: private header for the SiFive PDMA driver. It defines register offsets, control/status masks, transfer constants, channel/controller data structures, and platform quirk data used by `sf-pdma.c`.

Important APIs/types/functions: register constants describe per-channel control, transfer type/size, source/destination, active type, residue, and current-address registers. `struct pdma_regs` caches MMIO addresses. `struct sf_pdma_desc` wraps one virt-dma descriptor and transfer tuple. `enum sf_pdma_pm_state`, `struct sf_pdma_chan`, `struct sf_pdma`, and `struct sf_pdma_driver_platdata` define channel state, flexible-array controller state, and match-data quirks.

Control flow: `sf_pdma_setup_chans` fills `pdma_regs` from `SF_PDMA_REG_BASE`, initializes `sf_pdma_chan`, and binds each virtual channel to the shared `dma_device`. Transfer functions consume `sf_pdma_desc` fields and program corresponding registers.

State/persistence: all structures are runtime-only and allocated by probe. `PDMA_MAX_NR_CH` caps hardware channels at four; `MAX_RETRY` defines one error retry. Control masks define claim/run/interrupt/status bit usage.

Dependencies/integration: includes DMAEngine, dma-direction, internal DMAEngine helper, and virt-dma. It assumes 64-bit register accesses may be synthesized by the C file on architectures without `readq/writeq`.

Risks: `PDMA_BASE_ADDR` is defined but not used by the implementation, so register base comes from platform resources. Header-exposed fields such as `mappedbase`, `attr`, and DMA device address fields are currently unused, which can mislead future changes.

Test signals: compile with sparse/unused-field checks, verify channel count limits, register offsets against hardware manual, and exercise residue/current-address MMIO reads.
