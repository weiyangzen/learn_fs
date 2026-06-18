# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/coredump.c

## Purpose
This file implements MT7996 firmware crash dump collection and submission through Linux devcoredump. It captures metadata, firmware state, PC/LR stacks, and optional firmware memory regions.

## Important APIs, Types, And Functions
Exports are `mt7996_coredump_get_mem_layout()`, `mt7996_coredump_new()`, `mt7996_coredump_submit()`, `mt7996_coredump_register()`, and `mt7996_coredump_unregister()`. Internal helpers compute memory dump size, read firmware assert state, read firmware PC/LR stack logs, and build the final `mt7996_coredump` buffer. The `coredump_memdump` module parameter enables optional memory content.

## Control Flow
Registration allocates crash data and optional memory buffer sized from chip memory layout. On a crash, `mt7996_coredump_new()` requires `dump_mutex`, optionally waits for firmware dump state, assigns a GUID, and timestamps the event. Submit builds a vmalloc buffer, fills magic/kernel/fw/device/time metadata, reads assert count to label normal vs exception, reads current PC and stack logs, copies optional memory dump payload, unlocks, then passes the buffer to `dev_coredumpv()`. Unregister frees optional memory and crash data.

## State And Persistence
State lives in `dev->coredump.crash_data`, optional `memdump_buf`, GUID/timestamp, firmware dump registers, and devcoredump's retained userspace-visible blob. Memory region layout is static for MT7996 device IDs.

## Dependencies And Integration Points
It depends on `devcoredump`, `utsname`, GUID/time APIs, MT7996 register definitions, `dump_mutex`, and firmware recovery paths that call `mt7996_coredump_new()/submit()`.

## Risks
Optional memory dumping can allocate large vmalloc buffers and is gated by a module parameter. Locking must protect crash data while building the dump. Stack log register indexing and exception/non-exception stop/start behavior must match firmware debug hardware. `mt7996_coredump_register()` returns success without memory content if no layout is known, which callers must tolerate.

## Test Signals
Firmware assert trigger, normal manual dump, coredump with and without `coredump_memdump`, GUID/timestamp correctness, PC/LR stack population, userspace devcoredump readout, and unregister cleanup validate this file.
