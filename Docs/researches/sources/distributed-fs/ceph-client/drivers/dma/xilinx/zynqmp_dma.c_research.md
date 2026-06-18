# sources/distributed-fs/ceph-client/drivers/dma/xilinx/zynqmp_dma.c

## Purpose

This file implements the DMAengine memcpy driver for Xilinx ZynqMP DMA and AMD Versal Gen 2 DMA-compatible hardware. It exposes one DMA_MEMCPY channel per platform device, manages source and destination linked-list descriptors, handles interrupts and runtime power management, and registers an OF DMA controller.

## Important APIs, Types, and Functions

`struct zynqmp_dma_device` owns the DMAengine device, channel pointer, and main/APB clocks. `struct zynqmp_dma_chan` owns mapped registers, descriptor lists, a coherent low-level descriptor pool, software descriptor pool, IRQ, tasklet, idle/error flags, bus width, burst lengths, descriptor size, and an optional IRQ offset for Versal Gen 2. `struct zynqmp_dma_desc_sw` represents a submitted transaction and may link additional child descriptors through `tx_list`; each software descriptor points to paired source and destination `struct zynqmp_dma_desc_ll` hardware descriptors.

The DMAengine operations are `zynqmp_dma_prep_memcpy()`, `zynqmp_dma_tx_submit()`, `zynqmp_dma_issue_pending()`, `zynqmp_dma_alloc_chan_resources()`, `zynqmp_dma_free_chan_resources()`, `zynqmp_dma_device_terminate_all()`, `zynqmp_dma_synchronize()`, `dma_cookie_status`, and `zynqmp_dma_device_config()` for burst lengths. PM hooks use runtime suspend/resume to gate `clk_main` and `clk_apb`.

## Control Flow

Probe sets a 44-bit DMA mask, declares `DMA_MEMCPY`, initializes DMAengine callbacks, gets clocks, enables runtime PM, probes the channel, registers with DMAengine, registers OF DMA translation, and drops the runtime PM reference for autosuspend. Channel probe maps registers, validates `xlnx,bus-width` as 64 or 128 bits, reads optional match data for the IRQ register offset, detects `dma-coherent`, initializes lists and cookies, initializes hardware registers, requests the IRQ, and records descriptor size.

Resource allocation resumes the device, allocates `ZYNQMP_DMA_NUM_DESCS` software descriptors, initializes their async descriptors and free list, and allocates a coherent pool sized for paired source/destination low-level descriptors. `zynqmp_dma_prep_memcpy()` checks descriptor availability, chunks transfers by `ZYNQMP_DMA_MAX_TRANS_LEN`, obtains descriptors from the free list, programs linked-list source/destination descriptors, chains children into the first descriptor's `tx_list`, marks the final descriptor as end-of-descriptor, and returns the first async descriptor.

Submit assigns a cookie and, if a pending transaction already exists, patches the previous tail descriptor's next pointers to the new descriptor while clearing STOP bits. Issue pending starts the transfer only if idle: it programs SG mode and burst attributes, splices all pending descriptors into active, writes source/destination descriptor start addresses, enables interrupts, clears the byte counter, and enables the channel. IRQ handling acknowledges status, schedules the tasklet for done/error interrupts, sets `idle` on DONE, and clears overflow accounting. The tasklet resets on errors or completes as many descriptors as the destination accounting register reports, invokes callbacks, frees descriptors, and starts the next pending transfer when idle.

## State and Persistence

State is volatile and stored in lists plus hardware registers. `pending_list`, `active_list`, `done_list`, and `free_list` are protected by `chan->lock`. `desc_free_cnt` reserves descriptor capacity during prep. Hardware descriptor memory is coherent and reused between transfers. Runtime PM state gates clocks across allocation/free and probe/remove. There is no persistent configuration beyond DT properties and DMA slave burst settings.

## Dependencies and Integration Points

The driver depends on DMAengine, OF DMA, platform resources, PM runtime, clock framework, coherent DMA allocation, tasklets, and 64-bit MMIO write helpers. DT properties include `xlnx,bus-width`, optional `dma-coherent`, and compatible data for the Versal Gen 2 IRQ offset (`amd,versal2-dma-1.0`). Consumers get the single channel through OF translation regardless of DMA spec contents.

## Risks and Edge Cases

Descriptor accounting is critical: `zynqmp_dma_prep_memcpy()` decrements `desc_free_cnt` before all descriptors are obtained, and error paths must not leak reservations. `zynqmp_dma_get_descriptor()` assumes the free list is non-empty after the prior count check. Chaining new submissions onto pending tails mutates hardware descriptor STOP bits, so list/tail selection must stay consistent with child descriptors. Error IRQ handling resets the channel and frees all descriptors, which can surprise clients if partial completion expectations are wrong. Runtime PM error handling in allocation and probe has potential leak points if allocation fails after `pm_runtime_resume_and_get()`.

## Test Signals

Useful validation includes DMAengine memcpy tests across sizes below, equal to, and above `ZYNQMP_DMA_MAX_TRANS_LEN`; concurrent submissions that extend an existing pending chain; invalid/missing `xlnx,bus-width`; coherent versus noncoherent DT operation; runtime suspend/resume cycles; forced AXI/APB/overflow interrupts; and remove/shutdown while idle or after active transfers.
