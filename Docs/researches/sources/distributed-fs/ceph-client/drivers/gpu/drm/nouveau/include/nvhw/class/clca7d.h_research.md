# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clca7d.h

## Purpose
Defines the NVCA7D GB202 display core-channel method interface. It is the central method map for core display updates, head timing, SOR ownership/protocol, window routing/usage limits, cursor, CRC, LUT, and tile programming.

## Important APIs, Types, And Functions
Exports macros for `NVCA7D_UPDATE`, notifier controls, cursor/window/core interlocks, notifier surface addresses, `NVCA7D_SOR_SET_CONTROL`, `NVCA7D_WINDOW_*`, `NVCA7D_HEAD_*`, CRC/OLUT/cursor surface methods, and `NVCA7D_TILE_SET_TILE_SIZE`. The head block includes procamp/color-space, output-resource pixel depth, progressive/stereo/lock controls, pixel clocks, dither, display IDs, viewport/raster timing, cursor composition, CRC target selection, and OLUT parameters.

## Control Flow
There is no C control flow. Nouveau display code emits method sequences using these offsets, then uses `NVCA7D_UPDATE` to commit pending state. Interlock flags and update special-handling bits affect whether hardware coordinates core/window/cursor changes and whether interrupts or mode-switch paths are triggered.

## State And Persistence
No software state is stored here. The methods describe persistent display channel state in GPU hardware/context until a later atomic commit, suspend/resume replay, or channel destruction changes it.

## Dependencies And Integration Points
Used by NVIF pushbuffer helpers and DRM atomic display code for GB202-class display. It depends conceptually on `nvhw/drf.h` field packing and on `nvif/class.h` for `GB202_DISP_CORE_CHANNEL_DMA`.

## Risks
Display core methods are order-sensitive. Incorrect head ownership, lock-pin selection, SOR protocol, timing dimensions, cursor format/address, CRC buffer target, or LUT size can cause failed modesets, underruns, incorrect scanout, or display engine faults. The large generated macro surface also makes copy/paste or class-version mismatch errors likely.

## Test Signals
Signals include GB202 modeset success, atomic plane/cursor updates, SOR protocol selection for DP/HDMI FRL, vblank/CRC tests, LUT/dither tests, debug push traces, and absence of EVO method/trap reports.
