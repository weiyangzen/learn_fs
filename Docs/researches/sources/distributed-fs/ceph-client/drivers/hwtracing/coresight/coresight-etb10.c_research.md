# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-etb10.c

## Purpose
`coresight-etb10.c` implements the CoreSight Embedded Trace Buffer v1.0 sink. It can capture trace into on-chip RAM, expose captured data through a misc character device for sysfs-style sessions, and integrate with perf AUX buffers for perf sessions.

## Important APIs, Types, And Functions
`struct etb_drvdata` stores MMIO base, optional AT clock, CoreSight device, misc device, spinlock, single-reader flag, active PID, software dump buffer, hardware depth, and trigger counter. Hardware control is split into `__etb_enable_hw()`, `etb_enable_hw()`, `__etb_disable_hw()`, `etb_dump_hw()`, and `etb_disable_hw()`. CoreSight sink callbacks are `etb_enable()`, `etb_disable()`, `etb_alloc_buffer()`, `etb_free_buffer()`, and `etb_update_buffer()`.

User-space misc-device functions are `etb_open()`, `etb_read()`, and `etb_release()`. Sysfs exposes `trigger_cntr` and a `mgmt` register group. Probe registers the ETB as a CoreSight sink subtype `SINK_BUFFER`.

## Control Flow
Probe maps the AMBA resource, enables the AT clock, reads hardware buffer depth, allocates a software copy buffer, loads CoreSight platform data, clears stale claim tags, registers the CoreSight sink, and registers a misc device named after the CoreSight device. Sysfs enable rejects perf-owned sessions, claims hardware, clears RAM, programs trigger/formatter registers, enables capture, and sets mode. Perf enable rejects sysfs ownership, pins the monitored PID, sets up the perf buffer position, enables hardware, and increments refcounts.

Disable decrements `csdev->refcnt`; only the final disable flushes and stops the formatter, dumps ETB RAM into the software buffer, disclaims hardware, resets PID, and disables mode. Perf update stops capture, computes the readable region from RAM pointers and status, handles wrap/loss with barrier packets and `PERF_AUX_FLAG_TRUNCATED`, copies words into the AUX ring, resets RAM pointers, and re-enables capture.

## State And Persistence
Hardware state includes ETB RAM, read/write pointers, trigger counter, formatter control/status, and capture enable. Software state includes `drvdata->buf` for sysfs reads, `pid` ownership for perf, `local_t reading` for single misc-reader exclusion, `trigger_cntr`, and CoreSight mode/refcount.

## Dependencies And Integration Points
The driver depends on AMBA, CoreSight sink ops, ETM perf AUX buffer helpers, runtime PM, miscdevice, copy_to_user, circular buffer macros, claim tags, and the common CoreSight barrier packet. It integrates as a selectable default or explicit sink in CoreSight paths.

## Risks
Buffer pointer arithmetic is in ETB words in some paths and bytes in others; frame-size alignment handling is critical for decoders. Perf snapshot and non-snapshot modes intentionally differ in truncation behavior. `csdev->refcnt != 1` in update avoids stealing from shared sessions but can skip data. The misc-device lifetime comment relies on fops references after deregistration. Trigger counter store parses hex only.

## Test Signals
Tests should cover probe depth validation, sysfs capture/read, single-reader exclusion, perf allocation/update in snapshot and non-snapshot modes, wrap/full buffer handling, barrier insertion, formatter timeout logging, runtime PM, mode conflicts, and removal while the misc device has open file descriptors.
