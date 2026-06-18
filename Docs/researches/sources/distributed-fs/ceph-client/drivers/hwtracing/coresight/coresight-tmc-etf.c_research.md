# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etf.c

## Purpose
This file implements ETB/ETF-specific Trace Memory Controller behavior. ETB acts as a sink backed by embedded SRAM; ETF can act as both sink and link FIFO. The file supports sysfs capture, perf AUX capture, panic crash synchronization, and misc-device read preparation.

## Important APIs, Types, And Functions
Hardware helpers include `__tmc_etb_enable_hw()`, `tmc_etb_enable_hw()`, `tmc_etb_dump_hw()`, `__tmc_etb_disable_hw()`, `tmc_etb_disable_hw()`, `__tmc_etf_enable_hw()`, `tmc_etf_enable_hw()`, and `tmc_etf_disable_hw()`. Sink operations are `tmc_enable_etf_sink()`, `tmc_disable_etf_sink()`, `tmc_alloc_etf_buffer()`, `tmc_free_etf_buffer()`, and `tmc_update_etf_buffer()`. Link operations are `tmc_enable_etf_link()` and `tmc_disable_etf_link()`. Read lifecycle functions are `tmc_read_prepare_etb()` and `tmc_read_unprepare_etb()`.

## Control Flow And State
Sysfs sink enable allocates or reuses `drvdata->buf`, rejects concurrent reading, enables ETB circular-buffer mode, sets CoreSight mode, and increments refcount. Perf enable rejects sysfs mode and concurrent readers, associates the sink with one PID, configures perf buffer cursor state, and enables hardware if this is the first user for that PID. Perf update flushes and stops hardware, computes unread bytes from RRP/RWP/full status, aligns truncation to memory width, copies TMC RAM words into perf AUX pages, optionally inserts a barrier packet when data was lost, and re-enables hardware if the event remains active. Link mode uses ETF hardware FIFO mode. Panic sync copies embedded SRAM to reserved trace memory and writes validated crash metadata.

## Dependencies And Integration Points
The file depends on `coresight-tmc.h`, perf AUX buffer support, `coresight-etm-perf.h`, common TMC helpers, CoreSight modes/refcounts, crash metadata helpers, and barrier packet helpers from `coresight-priv.h`.

## Risks And Test Signals
Concurrency is guarded by `drvdata->spinlock`, `drvdata->reading`, CoreSight mode, refcount, and PID association. Incorrect refcounting can leave hardware enabled or block reads. Perf truncation must respect TMC memory-width alignment or hardware read pointers can become invalid. Panic sync must avoid trusting invalid reserved buffers and must maintain metadata write ordering before setting `valid`. Test signals include sysfs capture/read/re-enable, perf snapshot and non-snapshot AUX capture, truncation flag behavior, multiple perf events for same and different PIDs, ETF link FIFO paths, concurrent read rejection, panic crashdata generation, and full-buffer barrier insertion.
