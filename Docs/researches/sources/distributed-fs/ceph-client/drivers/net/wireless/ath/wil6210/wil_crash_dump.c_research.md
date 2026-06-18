# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_crash_dump.c

## Purpose
This file implements firmware crash dump extraction for wil6210. It computes the host-address span covering all firmware mapping sections marked for crash dump, copies those regions from device memory into a contiguous buffer, and publishes the result through Linux `dev_coredumpv()`.

## Important APIs, Types, and Functions
- `wil_fw_get_crash_dump_bounds()` scans `fw_mapping[]` for `crash_dump` sections and returns total dump size plus optional minimum host address.
- `wil_fw_copy_crash_dump()` validates destination size, locks device memory access, rejects suspend/suspended state, copies each crash-dump mapping with `wil_memcpy_fromio_32()`, and unlocks.
- `wil_fw_core_dump()` allocates a vmalloc-backed dump buffer, copies the dump, and transfers ownership to the devcoredump subsystem.

## Control Flow
On firmware crash or recovery, callers invoke `wil_fw_core_dump()` or the lower-level copy API. Bounds are calculated first. Core dump allocation uses `vzalloc()`. Copying takes `wil->mem_lock` for write, checks suspend state, iterates over every `fw_mapping` entry with `crash_dump` set, computes its destination offset relative to the minimum host address, copies from `wil->csr + HOSTADDR(map->host)`, then releases the lock. `dev_coredumpv()` owns and later frees the buffer after successful publication.

## State and Persistence Behavior
The generated dump is transient kernel memory handed to devcoredump; it is not written directly by this file. Source state is the global `fw_mapping[]` table and the device memory window `wil->csr`. The function preserves holes between mapped sections by using a contiguous host-address span, so unmapped gaps remain zero from `vzalloc()` in the core-dump path.

## Dependencies and Integration Points
The file depends on `wil6210.h`, firmware mapping metadata populated elsewhere, `wil_memcpy_fromio_32()`, `HOSTADDR()`, `wil->mem_lock`, status bits for suspend state, and Linux `devcoredump`. Platform recovery code may call the exported copy function through platform callbacks.

## Risks
The first mapping seeds bounds even if it is not marked `crash_dump`, so mapping table ordering and flags matter. Size arithmetic assumes mapping ranges are valid and non-overflowing. Copying during suspend is explicitly blocked, but callers must handle `-EBUSY`. Because destination layout is based on host addresses, consumers need mapping knowledge to interpret sections. Failure to keep `fw_mapping[]` synchronized with hardware versions can omit important crash regions or read invalid memory.

## Test Signals
Trigger firmware crash recovery and verify a devcoredump appears with expected size and non-zero mapped sections. Test low-memory allocation failure, too-small destination buffers via `wil_fw_copy_crash_dump()`, suspend-in-progress rejection, and hardware variants with different `fw_mapping[]` tables.
