# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_startstop.h

## Purpose
Declares the common firmware processor start and stop APIs.

## Important APIs, types, and functions
- Forward declares `struct pvr_device`.
- Declares `pvr_fw_start()` and `pvr_fw_stop()`.

## Control flow
No runtime flow exists in the header. It exposes start/stop sequencing to common firmware initialization and teardown.

## State and persistence
No state is stored here. The declared functions mutate hardware register state and firmware boot state in their implementation.

## Dependencies and integration points
Included by `pvr_fw.c` and implemented by `pvr_fw_startstop.c`. It keeps hardware sequencing separate from common firmware object allocation.

## Risks
Signature changes affect firmware init unwind paths. The header hides all processor/platform-specific details, which is appropriate for keeping callers from depending on reset internals.

## Test signals
Build coverage catches declaration drift. Runtime validation belongs to `pvr_fw_start()` and `pvr_fw_stop()` boot/shutdown tests.
