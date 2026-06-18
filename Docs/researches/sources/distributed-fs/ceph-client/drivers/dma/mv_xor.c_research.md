<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c

## Purpose
DMAEngine/async_tx driver for Marvell XOR engines. It offloads memcpy, XOR, and interrupt operations, primarily for RAID/async_tx acceleration, across Orion and Armada variants.

## Important APIs, Types, And Functions
The file uses `struct mv_xor_device`, `struct mv_xor_chan`, and `struct mv_xor_desc_slot` from `mv_xor.h`. Descriptor helpers initialize hardware descriptors, set operation mode, next pointer, and source addresses. `mv_xor_tx_submit`, `mv_chan_slot_cleanup`, `mv_xor_tasklet`, `mv_xor_status`, and `mv_xor_issue_pending` manage descriptor chains and cookies. Prep functions implement DMA_XOR, DMA_MEMCPY as one-source XOR, and DMA_INTERRUPT as a dummy minimum XOR. Probe/channel-add code configures MBUS windows, maps resources, allocates descriptor pools and dummy buffers, runs self-tests, registers per-channel DMA devices, and handles suspend/resume state.

## Control Flow
Probe maps low/high XOR register regions, determines hardware variant from DT or platform data, configures MBUS windows, enables an optional clock, limits engines/channels by CPU count, and adds each channel from DT children or platform data. Channel add maps dummy buffers, allocates a write-combined descriptor pool, installs DMAEngine callbacks based on capabilities, requests IRQ, configures operation mode, initializes lists/cookies/tasklet, runs memcpy and XOR self-tests when enabled, then registers the DMA device. Prep allocates a descriptor slot from the free list, initializes the hardware descriptor, validates/creates MBUS windows for IO addresses, and returns an async descriptor. Submit assigns a cookie, appends to the chain, links the previous hardware descriptor if needed, and starts a new chain if hardware is idle. Issue-pending activates hardware once the pending threshold is reached. IRQ logs errors, schedules the tasklet, and clears completion causes. Cleanup scans the chain for successful descriptors, unmaps, invokes callbacks, runs dependencies, moves slots to completed or free lists based on ack state, updates completed cookies, and restarts pending descriptors if the engine is idle.

## State And Persistence
State includes hardware descriptor pool memory, chain/free/allocated/completed slot lists, pending activation counter, dummy DMA mappings, saved suspend registers, cached MBUS windows, channel cookies, and XOR engine registers. It persists only for the driver/channel lifetime.

## Dependencies And Integration Points
Depends on DMAEngine and async_tx APIs, platform data or OF child nodes, IRQs, optional clocks, Marvell MBUS helpers (`mv_mbus_dram_info`, `mvebu_mbus_get_io_win_info`), coherent/write-combined DMA memory, and platform compatible strings for Orion, Armada 380, and Armada 3700. Built in through `builtin_platform_driver`.

## Risks And Edge Cases
The driver uses `BUG()`/`BUG_ON()` in descriptor mode paths and length limits, so invalid internal state can panic the kernel. `mv_xor_add_io_win` dynamically consumes a limited set of MBUS windows and can fail with `-ENOMEM`. Self-tests sleep for fixed short intervals and can disable a slow but otherwise functional channel. DMA_INTERRUPT relies on dummy buffers mapped for the driver lifetime. Error handling ignores decode errors but warns on other hardware errors; cleanup relies on descriptor success bits and current descriptor reads to avoid freeing active slots. The global `mv_xor_engine_count` is declared but not incremented in this file, so engine limiting may be ineffective depending on external context.

## Test Signals
Boot/probe self-tests for memcpy and XOR are strong signals. Additional coverage should use async_tx RAID/XOR workloads, dmatest memcpy, interrupt-only descriptors, IO-window address targets, suspend/resume register restoration, descriptor pool exhaustion, IRQ error causes, and both descriptor-mode and register-mode hardware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mv_xor.c -->
