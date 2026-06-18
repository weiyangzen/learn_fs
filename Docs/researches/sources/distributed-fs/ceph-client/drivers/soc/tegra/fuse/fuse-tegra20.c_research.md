# sources/distributed-fs/ceph-client/drivers/soc/tegra/fuse/fuse-tegra20.c

## Purpose

`fuse-tegra20.c` supplies the Tegra20-specific fuse backend. Tegra20 needs APBDMA for safe runtime fuse reads, while early boot reads use direct MMIO. The file also seeds kernel randomness from SKU, straps, chip ID, process IDs, speedo IDs, and unique ID fuse words.

## Important APIs, Types, and Functions

The SoC descriptor is `tegra20_fuse_soc`. It uses `tegra20_fuse_init()` as the early init hook, `tegra20_fuse_probe()` as the runtime probe hook, and `tegra20_fuse_info` to describe a 0x1f8-byte fuse aperture with spare bits at offset 0x100.

`tegra20_fuse_read_early()` directly reads `FUSE_BEGIN + offset`. `tegra20_fuse_read()` performs a DMA_DEV_TO_MEM transfer from the fuse physical address into one coherent 32-bit buffer. `apb_dma_complete()` completes the wait object, and cleanup helpers release the APBDMA channel and coherent buffer through devm actions.

## Control Flow

Early init sets `fuse->read_early`, initializes revision data, calls Tegra20 speedo binning, and calls `tegra20_fuse_add_randomness()`. Runtime probe requests a DMA slave channel filtered to `nvidia,tegra20-apbdma`, allocates a coherent one-word buffer, initializes slave config, completion, and mutex, and installs `fuse->read = tegra20_fuse_read`.

Each runtime read resumes the fuse device, serializes through `apbdma.lock`, programs the source address, configures the DMA channel, prepares a one-word slave transfer, waits up to 50 ms, terminates on timeout, copies the value from the coherent buffer, unlocks, and drops runtime PM.

## State and Persistence Behavior

Runtime persistent state is the Tegra20 `apbdma` substructure in `struct tegra_fuse`: DMA channel, slave config, one-word coherent buffer, completion, and mutex. Fuse data itself is immutable hardware OTP. The file mutates the global `tegra_sku_info` indirectly via `tegra_init_revision()` and `tegra20_init_speedo_data()`.

## Dependencies and Integration Points

The backend depends on DMAengine, coherent DMA allocation, runtime PM, APBDMA device-tree compatibility, Tegra APBMISC/fuse public helpers, and speedo code in `speedo-tegra20.c`. The common driver calls the SoC hooks and NVMEM eventually exposes reads through this backend.

## Risks and Edge Cases

Runtime reads return zero if `pm_runtime_resume_and_get()` fails because the error is returned as `u32`. DMA setup failures also fall through to zero. That behavior can hide transient read errors from NVMEM consumers. The DMA channel filter accepts by controller compatible only, so systems with multiple matching channels rely on DMAengine channel allocation policy. Timeout warns and terminates the channel, but callers see zero rather than an error.

## Test Signals

Test APBDMA probe deferral, coherent allocation failure handling, NVMEM reads across the full Tegra20 fuse range, runtime suspend/resume around repeated reads, 50 ms timeout fault injection, early UID randomness contribution, and correct speedo/revision output on Tegra20 boards.
