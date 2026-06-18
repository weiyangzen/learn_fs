# sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_2.c

## Purpose

`cumana_2.c` is the Cumana SCSI II expansion-card driver. It wraps the generic FAS216 core, provides real DMA and pseudo-DMA support, controls bus termination, exposes proc write/show hooks, and registers the expansion-card driver.

## Important APIs, Types, and Functions

`struct cumanascsi2_info` embeds `FAS216_Info`, card/base pointers, terminator state, and a fixed SG array. Board hooks are `cumanascsi_2_irqenable()`, `cumanascsi_2_irqdisable()`, `cumanascsi_2_terminator_ctl()`, `cumanascsi_2_intr()`, `cumanascsi_2_dma_setup()`, `cumanascsi_2_dma_pseudo()`, and `cumanascsi_2_dma_stop()`. Reporting/configuration uses `cumanascsi_2_info()`, `cumanascsi_2_set_proc_info()`, and `cumanascsi_2_show_info()`. Lifecycle is `cumanascsi2_probe()` and `cumanascsi2_remove()`.

## Control Flow

Probe maps MEMC space, allocates a host, stores drvdata, applies slot-based module parameter `term[]`, configures FAS216 timing and callbacks, installs expansion-card IRQ ops, initializes FAS216, requests IRQ and optional DMA channel, enables DMA capability when available, then calls `fas216_add()`. Runtime command processing is `fas216_queue_command`; interrupts call `fas216_intr()`.

DMA setup disables card DMA, then either maps the current SCSI pointer into the fixed SG array and programs the platform DMA channel for sufficiently large or required transfers, or falls back to pseudo/PIO. Pseudo-DMA implements reads from the board FIFO; the write pseudo-DMA branch is disabled and prints `PSEUDO_OUT???`.

## State and Persistence Behavior

Persistent runtime state is per host: terminator flag, fixed SG list, embedded FAS216 queues/device state, and optional DMA channel ownership. The `term[]` module parameter supplies initial per-slot termination but is not persisted.

## Dependencies and Integration Points

The file depends on FAS216 core APIs, `arm_scsi.h` for `copy_SCp_to_sg()`, ARM DMA APIs, ecard IRQ hooks, Linux SCSI host APIs, and optional proc write support via the host template.

## Risks and Edge Cases

`dma_map_sg()` return value is ignored and the driver does not visibly unmap SG mappings in `dma_stop()`, which should be checked against platform DMA expectations. The pseudo-DMA data-out path is effectively unimplemented, so fallback writes can fail or only log. `copy_SCp_to_sg()` can BUG if SG count exceeds `NR_SG`. Termination can be modified via proc-style input with minimal parsing.

## Test Signals

Validate slot-based termination, proc `term=0/1`, IRQ enable/disable, real DMA read/write above 512 bytes, fallback PIO/pseudo reads below threshold, behavior when DMA request fails, FAS216 disconnect/sync negotiation, and clean resource release for IRQ and DMA on probe failure and remove.
