# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.c

## Purpose
`pmc.c` implements the Performance Monitoring Counters capture buffer controlled through debugfs. It allocates a DMA descriptor ring and descriptor buffers, tells firmware to start/stop PMC capture with WMI commands, and exposes captured buffers/ring bytes to userspace.

## Important APIs, Types, And Functions
`struct desc_alloc_info` stores descriptor DMA address and virtual address. `wil_pmc_init()` clears and initializes `wil->pmc`. `wil_pmc_alloc()` validates descriptor count/size, allocates descriptor metadata, allocates a coherent p-ring, allocates each coherent descriptor buffer, initializes buffers with `PCM_DATA_INVALID_DW_VAL | index`, configures `vring_tx_desc` entries, and sends `WMI_PMC_ALLOCATE`. `wil_pmc_free()` optionally sends `WMI_PMC_RELEASE` and frees all coherent memory. Read APIs are `wil_pmc_read()`, `wil_pmc_llseek()`, and `wil_pmcring_read()`.

## Control Flow
All operations lock `pmc->lock`. Allocation refuses double allocation and invalid/overflowing dimensions, temporarily switches coherent DMA mask to 32-bit when the device was initialized with a wider mask because vring addresses must share upper bits, then restores the original mask. Error paths free partially allocated descriptors and ring memory. Reads map file position to descriptor index and offset, then copy from the current descriptor only; seeking clamps to PMC size.

## State And Persistence
PMC state persists in `wil->pmc`: allocation flag via `pring_va`, descriptor count/size, p-ring DMA/VA, descriptor array, and `last_cmd_status`. Captured data remains in coherent DMA buffers until freed or device teardown. `debugfs.c` frees PMC on debugfs removal/reset teardown.

## Dependencies And Integration Points
The file depends on DMA coherent allocation, WMI PMC commands, TX/RX descriptor layout, debugfs file operations declared in `pmc.h`, and the main VIF MID for WMI sends. It is controlled through debugfs `pmccfg`, `pmcdata`, and `pmcring`.

## Risks
Large descriptor counts/sizes can consume substantial coherent memory, though count and multiplication overflow are checked. The DMA mask switch assumes restoring the prior mask cannot fail. `wil_pmc_read()` only reads within a single descriptor per call, so userspace must continue reading across descriptor boundaries. Firmware release failures do not prevent memory cleanup.

## Test Signals
Test invalid dimensions, maximum ring size, allocation failure at each stage, double alloc/free without alloc, read/seek boundaries, descriptor-boundary reads, 32-bit DMA-mask systems and wider DMA-mask systems, WMI allocate/release failure, and teardown while PMC is allocated.
