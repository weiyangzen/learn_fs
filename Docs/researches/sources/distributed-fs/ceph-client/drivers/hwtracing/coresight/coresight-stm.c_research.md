# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-stm.c

## Purpose
This file implements the CoreSight System Trace Macrocell driver. STM is a software and hardware event trace source that exposes stimulus ports through the generic Linux STM framework and registers as a CoreSight source.

## Important APIs, Types, And Functions
`struct stm_drvdata` stores programming MMIO, stimulus channel space, clocks, CoreSight and generic STM objects, trace ID, port/event register caches, channel count, write granularity, and the guaranteed-channel bitmap. CoreSight source operations are `stm_enable()`, `stm_disable()`, and `stm_trace_id()`. Generic STM integration uses `stm_generic_packet()`, `stm_mmio_addr()`, `stm_generic_link()`, `stm_generic_unlink()`, and `stm_generic_set_options()`. Sysfs attributes expose hardware event enable/select, port enable/select, and trace ID. Probe is handled by `__stm_probe()` for AMBA and platform devices.

## Control Flow And State
Probe maps the programming resource and the separate stimulus resource, determines 32-bit versus 64-bit writes from `STMSPFEAT2R`, determines stimulus port count from boot parameter or `CORESIGHT_DEVID`, allocates the guaranteed bitmap, registers with the generic STM subsystem, gets CoreSight platform data, registers as a software source, and allocates a system trace ID. `stm_enable()` only accepts sysfs mode, takes CoreSight mode ownership, powers the device, and programs event tracing, stimulus ports, synchronization, timestamping, and global enable. Packet writes verify the source is enabled, validate channel number, derive packet address from packet type and options, clamp size to supported write width, and perform aligned writes.

## Dependencies And Integration Points
The driver depends on AMBA/platform buses, runtime PM, generic STM APIs, CoreSight trace-id allocation, firmware stimulus-area description, and `coresight_enable_sysfs()`/`coresight_disable_sysfs()` for generic STM link/unlink. It integrates with perf only indirectly through CoreSight path mode checks; direct enable rejects non-sysfs modes.

## Risks And Test Signals
Stimulus mapping is firmware-sensitive: DT requires `stm-stimulus-base`, while ACPI expects the second memory resource. Packet writes are marked `notrace` and must avoid recursion or sleeping. Channel option changes are rejected unless tracing is enabled, and out-of-range channels fail. Trace ID acquisition failure unwinds CoreSight and STM registration. Test signals include generic STM character/device writes, sysfs enable/disable, channel guaranteed/invariant options, 32-bit and 64-bit packet writes, boot `boot_nr_channel`, OF/ACPI resource parsing, and runtime PM clock failure unwinds.
