# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/log.h

## Purpose
Declares NVIF logging-buffer tracking helpers, including global GSP log tracking.

## Important APIs, Types, And Functions
Defines `struct nvif_log`, `struct nvif_logs`, `NVIF_LOGS_DECLARE`, `nvif_log_shutdown()`, and external `gsp_logs`.

## Control Flow
`nvif_log_shutdown()` walks the list of logs and calls each entry's shutdown callback; callbacks are expected to remove their own list entries.

## State And Persistence
`nvif_logs` persists as a list root; each `nvif_log` tracks a backing logging resource until module exit or shutdown.

## Dependencies And Integration Points
Depends on kernel list APIs through NVIF OS headers and integrates with GSP logging allocation/cleanup.

## Risks
Shutdown callbacks must delete entries safely. Missing removal can loop or double-free; missing shutdown leaks log buffers.

## Test Signals
GSP log allocation, module unload cleanup, KASAN/list-debug checks, and repeated init/fini validate behavior.
