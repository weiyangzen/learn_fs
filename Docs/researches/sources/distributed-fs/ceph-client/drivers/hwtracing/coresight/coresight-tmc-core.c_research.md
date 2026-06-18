# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-core.c

## Purpose
This file implements common probe, userspace read, crashdata, sysfs attribute, and bus-registration logic for CoreSight Trace Memory Controller devices. It handles ETB, ETF, and ETR variants and delegates variant-specific trace capture to ETF/ETR helpers.

## Important APIs, Types, And Functions
Common hardware helpers are `tmc_wait_for_tmcready()`, `tmc_flush_and_stop()`, `tmc_enable_hw()`, `tmc_disable_hw()`, and `tmc_get_memwidth_mask()`. File operations `tmc_open()`, `tmc_read()`, and `tmc_release()` expose captured trace through a misc device. Crashdata operations expose reserved-memory trace from a previous boot. Probe logic in `__tmc_probe()` reads `CORESIGHT_DEVID`, determines config type and memory width, sets buffer size and ETR burst/capability data, maps reserved crash buffers, registers CoreSight device operations, and registers misc devices. Sysfs attributes expose trigger counter, buffer size, stop-on-flush, and management registers.

## Control Flow And State
For normal reads, open calls variant-specific read prepare, read copies trace slices to userspace, and release unprepares. Reserved crashdata validation checks buffer presence, metadata version, valid bit, trace physical address, metadata CRC, and trace-data CRC. If valid, metadata is converted into a readable circular-buffer view and a `crash_<name>` misc device is registered. Probe chooses ETB as sink buffer, ETF as link-sink FIFO, or ETR as sysmem sink based on hardware config bits.

## Dependencies And Integration Points
The file depends on AMBA/platform buses, reserved-memory OF helpers, DMA mask setup, miscdevice, runtime PM, `coresight-tmc.h`, ETF/ETR operation tables, CoreSight platform data, and CoreSight claim/access helpers. It integrates with ETR scatter-gather capability detection and SoC-600 UCI data.

## Risks And Test Signals
There is a notable risk in the `out:` path: crashdata validation is attempted even when earlier probe setup failed, so fields must be safe after partial initialization. Reserved-memory mappings can partially succeed, and crash metadata trust is guarded by version/address/CRC checks. Buffer-size writes are allowed only for ETR and require page alignment. Test signals include ETB/ETF/ETR probe, unsupported config rejection, misc read lifecycle, valid and invalid crash metadata, reserved-memory wraparound, ETR DMA mask selection, scatter-gather firmware properties, and runtime PM clock behavior.
