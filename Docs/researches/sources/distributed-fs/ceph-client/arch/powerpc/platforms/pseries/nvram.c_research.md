# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/nvram.c

## Purpose
Provides pSeries NVRAM access through RTAS fetch/store calls and integrates NVRAM partitions with RTAS error logging and oops/pstore preservation.

## Important APIs, Types, And Functions
Important functions are `pSeries_nvram_read`, `pSeries_nvram_write`, `pSeries_nvram_get_size`, `nvram_write_error_log`, `nvram_read_error_log`, `nvram_clear_error_log`, `clobbering_unread_rtas_event`, `pseries_nvram_init_log_partitions`, and `pSeries_nvram_init`. Static state includes `nvram_size`, RTAS tokens, `nvram_buf`, `nvram_lock`, and unread event timestamps.

## Control Flow
Initialization finds the OF `nvram` node, reads `#bytes`, caches RTAS tokens, and installs `ppc_md` NVRAM callbacks. Reads and writes clamp the request to NVRAM size, serialize on a spinlock, chunk transfers to 32 bytes, and call RTAS with a low physical address buffer. Log partition initialization scans NVRAM, initializes RTAS and oops partitions, and records unread event timing on writes.

## State And Persistence
NVRAM contents are persistent firmware storage. Kernel state tracks size, service tokens, a shared transfer buffer, and timestamps for unread RTAS events. `last_rtas_event` is also exported under `CONFIG_PSTORE`.

## Dependencies And Integration Points
Depends on RTAS NVRAM services, OF NVRAM node data, `ppc_md` machine callbacks, generic PowerPC NVRAM partition helpers, RTAS log partition definitions, pstore when enabled, and timekeeping.

## Risks And Edge Cases
The static transfer buffer is protected by a spinlock because RTAS accesses are serialized and physically addressed. Partial or mismatched RTAS byte counts are treated as I/O errors. `nvram_clear_error_log` marks an event logged rather than erasing it. Oops logging can clobber an unread RTAS event if both partitions overlap, so `clobbering_unread_rtas_event` uses a short timeout heuristic.

## Test Signals
Boot with a valid and missing NVRAM node, read/write `/dev/nvram` through machine callbacks, validate partition scanning, inject RTAS fetch/store failures, test RTAS event write/read/clear, and verify oops/pstore behavior when oops and RTAS log partitions share storage.
