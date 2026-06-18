# sources/distributed-fs/ceph-client/drivers/block/n64cart.c

## Purpose
This file implements a tiny read-only block driver for Nintendo 64 cartridge data exposed through a platform device. It maps the PI registers, uses DMA to copy cartridge ranges into bio pages, and publishes one `n64cart` disk without partition scanning.

## Important APIs, Types, And Functions
Module parameters `start` and `size` define the cartridge byte range. Register helpers `n64cart_write_reg()`, `n64cart_read_reg()`, and `n64cart_wait_dma()` drive the PI DMA engine. `n64cart_do_bvec()` maps each bio vector for DMA, programs DRAM address, cartridge address, and DMA length, waits for completion, and unmaps. `n64cart_submit_bio()` iterates all bio segments and ends or errors the bio. `n64cart_probe()` allocates and registers the gendisk. `n64cart_init()` registers a probe-only platform driver.

## Control Flow
During init, `platform_driver_probe()` calls `n64cart_probe()`. Probe validates that `start` and `size` are provided and that size is 4 KiB aligned, maps the register resource with devm, allocates a disk with 4 KiB logical/physical block sizes, marks it read-only and no-partition, sets capacity from `size`, and adds it. For each bio, the driver computes the byte offset from the sector, processes each segment by DMAing from `start + pos`, and calls `bio_endio()` once all segments succeed.

## State And Persistence Behavior
The driver keeps only global `reg_base`, `start`, and `size`. The underlying cartridge data is persistent/ROM-like and the disk is explicitly read-only. There is no dynamic removal path, no private disk allocation retained for unload, and no write handling beyond the read-only block-layer flag.

## Dependencies And Integration Points
It depends on platform-device resources, MMIO accessors, DMA mapping for bio vectors, blkdev/gendisk APIs, and module parameters. It integrates as an embedded boot-time platform driver rather than a hot-unpluggable module.

## Risks
The driver busy-waits on DMA status with `cpu_relax()` and has no timeout. Alignment is only WARNed for bvec offset/length rather than rejected. The comment states no module/unload support; the disk pointer is not stored for remove, so this is intended for constrained embedded boot use. Incorrect `start` or `size` parameters can expose the wrong cartridge region.

## Test Signals
Expected signals are failure on missing parameters, failure on non-4K size, successful `n64cart` read-only disk registration, correct capacity, successful reads of aligned blocks, no write acceptance, and stable behavior under multi-segment bios.
