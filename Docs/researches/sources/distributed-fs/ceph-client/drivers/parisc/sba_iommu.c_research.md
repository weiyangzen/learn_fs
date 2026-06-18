# sources/distributed-fs/ceph-client/drivers/parisc/sba_iommu.c

## Purpose
This file is the PA-RISC System Bus Adapter IOMMU driver for Astro, Ike, REO, Pluto, and related IOC hardware. It initializes I/O page directories, allocates IOVA ranges, implements the platform DMA mapping API, programs LBA IBASE/IMASK registers, exposes diagnostic procfs files, and reports LMMIO routing ranges to PCI host bridges.

## Important APIs, Types, And Functions
DMA operations are collected in `sba_ops`: `sba_dma_supported()`, `sba_alloc()`, `sba_free()`, `sba_map_phys()`, `sba_unmap_phys()`, `sba_map_sg()`, and `sba_unmap_sg()`. IOVA allocation helpers include `sba_search_bitmap()`, `sba_alloc_range()`, `sba_free_range()`, `sba_io_pdir_entry()`, and `sba_mark_invalid()`. Initialization helpers include `sba_alloc_pdir()`, `setup_ibase_imask()`, `sba_ioc_init_pluto()`, `sba_ioc_init()`, `sba_hw_init()`, `sba_common_init()`, and `sba_driver_callback()`. External integration APIs are `sba_get_iommu()`, `sba_directed_lmmio()`, and `sba_distributed_lmmio()`.

## Control Flow
`sba_init()` registers the PA-RISC IOA/BCPORT driver. Probe maps the SBA, identifies the chip revision, allocates `struct sba_device`, initializes IOC locks, reads PAT resources if applicable, resets risky firmware-initialized devices when needed, configures IOC control and rope hard-fail behavior, initializes one or two IOCs, allocates PDIRs/resource bitmaps, sets `hppa_dma_ops`, and creates procfs diagnostics. DMA mapping allocates aligned IOVA bitmap ranges under `res_lock`, writes little-endian valid PDIR entries with coherence index data, syncs FDC operations when required, and returns an IOVA. Unmapping clears valid bits, purges the I/O TLB through `IOC_PCOM`, frees bitmap ranges, and flushes purge writes. SG mapping shares the common two-pass coalesce/fill helpers from `iommu-helpers.h`.

## State And Persistence
Global state includes `sba_list`, `global_ioc_cnt`, `ioc_needs_fdc`, `piranha_bad_128k`, and optional AGP reservation state. Each IOC persists `ioc_hpa`, `pdir_base`, `pdir_size`, `res_map`, search hints, base/mask fields, locks, and optional statistics. Hardware state includes IOC PDIR base, IBASE/IMASK, page-size config, PCOM purges, rope controls, and LBA IBASE/IMASK routing programmed via child LBA callbacks.

## Dependencies And Integration Points
The driver depends on Linux DMA map ops, scatterlist APIs, PA-RISC PDC/PAT/model data, page-zero firmware records, LBA register programming through `lba_set_iregs()`, Linux procfs, IOMMU bitmap boundary helpers, and architecture-specific cache/IO flush instructions. LBA uses `sba_get_iommu()` and LMMIO routing helpers during PCI setup.

## Risks
This is hardware-workaround-heavy code. Wrong PDIR alignment or resource bitmap state can cause DMA data corruption or IOMMU faults. PA8700/Piranha bad-region handling depends on physical allocation behavior. `global_ioc_cnt` calculation uses a suspicious boolean condition that may not count Astro/Pluto as intended. DMA map/unmap paths assume the device can be resolved to an IOC; null devices are rejected or BUG. SG coalescing depends on virtual contiguity and correct segment-boundary math. Procfs diagnostic functions only show the first IOC.

## Test Signals
Signals include successful SBA discovery, DMA API operation for PCI devices, stress tests for map/unmap single and SG, no PDIR bitmap leaks, correct IOTLB purges, stable operation with USB reset paths, LBA resource routing correctness, `/proc/bus/runway/sba_iommu` or `/proc/bus/mckinley/sba_iommu` output, and high-load network/storage DMA tests. Hardware-specific tests should cover Astro, Ike/REO, Pluto, PA8700 bug cases, and AGP reservation.
