# sources/distributed-fs/ceph-client/drivers/remoteproc/st_slim_rproc.c

## Purpose
Provides exported allocation and teardown helpers for ST SLIM-core based devices that want to register a SLIM core as a remoteproc. It maps SLIM memories/registers, manages clocks, starts/stops the core, and supports ELF segment loading into IMEM/DMEM.

## Important APIs, Types, And Functions
Exports `st_slim_rproc_alloc()` and `st_slim_rproc_put()`. Internal ops are `slim_rproc_start()`, `slim_rproc_stop()`, and `slim_rproc_da_to_va()`. `slim_rproc_ops` supplies start/stop, address translation, ELF boot address, load, and sanity-check callbacks.

## Control Flow
`st_slim_rproc_alloc()` validates firmware name and DT compatibility, allocates an rproc, maps `dmem`, `imem`, `slimcore`, and `peripherals`, acquires/enables clocks, registers the rproc, and returns the SLIM handle. Start resets and ungates the CPU pipeline, disables STBus sync, clears/masks command and interrupt registers, enables the CPU, and logs hardware/firmware revisions. Stop masks channels, gates the pipeline clock, clears run enable, and warns if the core remains enabled.

Address translation maps exact IMEM/DMEM bus addresses to ioremapped CPU addresses when the requested length fits the region.

## State And Persistence Behavior
Clocks stay enabled between alloc and put, while start/stop manipulates SLIM control registers. I/O mappings are devm-managed. The rproc exists until `st_slim_rproc_put()` disables clocks, puts them, calls `rproc_del()`, and frees the rproc. There is no resource-table parser in this helper.

## Dependencies And Integration Points
Depends on a parent platform driver, resources named `dmem`, `imem`, `slimcore`, and `peripherals`, compatible `st,slim-rproc`, clock providers, remoteproc core, and ELF loader helpers.

## Risks
`slim_rproc_da_to_va()` only matches segment addresses equal to a memory region base, so firmware segment layouts with offsets may fail. Keeping clocks enabled outside start/stop affects power. Stop uses register writes rather than reset controls and only warns if disable fails. No mailbox/rpmsg integration is present here.

## Test Signals
Cover missing firmware name, incompatible DT, missing memory resources, deferred clocks, ELF segment load into IMEM/DMEM, start/stop register sequencing, firmware revision read from DMEM, repeated alloc/put cleanup, and segment addresses with offsets.
