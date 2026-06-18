# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/debug.h

## Purpose
Defines NVKM debug verbosity levels.

## Important APIs, Types, And Functions
Exports `NV_DBG_FATAL`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `TRACE`, `PARANOIA`, and `SPAM`.

## Control Flow
No executable flow. Logging macros compare device/client debug levels against these constants.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
Used by NVKM/NVIF logging macros throughout the driver.

## Risks
Changing numeric ordering changes filtering semantics globally.

## Test Signals
Debug option parsing and expected log filtering validate behavior.
