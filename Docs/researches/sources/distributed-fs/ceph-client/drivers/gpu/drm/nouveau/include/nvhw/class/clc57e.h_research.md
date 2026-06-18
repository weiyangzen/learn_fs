# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57e.h

## Purpose
Defines the NVC57E display window-channel method interface used to build EVO/display pushbuffer commands for legacy Volta/Turing/Ampere-style window channels.

## Important APIs, Types, And Functions
This header exports only macros. Important method groups are `NVC57E_SET_SIZE`, `NVC57E_SET_STORAGE`, `NVC57E_SET_PARAMS`, planar storage/context/offset/point methods, `NVC57E_SET_PRESENT_CONTROL`, color-format conversion coefficients, and ILUT context/offset/control. Format constants cover RGB, packed YUV, planar/semi-planar YUV, 10/12/16-bit, and floating-point formats.

## Control Flow
There is no executable control flow. Callers sequence these method offsets through NVIF push helpers, usually writing surface size/storage, format parameters, source/destination rectangles, present control, and optional color conversion or ILUT state before kicking the display channel.

## State And Persistence
The file stores no C state. The values program display channel state in GPU context memory or display hardware; state persists until overwritten by a later pushbuffer update or channel teardown.

## Dependencies And Integration Points
Integrated by display code that emits pushbuffer methods through `nvif/push*.h` and class IDs from `nvif/class.h`. The bit ranges are consumed by `NVVAL`/`NVDEF` helpers from `nvhw/drf.h`.

## Risks
Method offsets and bitfields are hardware ABI. Incorrect format, storage layout, block height, pitch, or address handling can produce scanout corruption, invalid display flips, or GPU channel faults.

## Test Signals
Build coverage for macro references, successful modesets and plane updates, correct RGB/YUV formats, ILUT behavior, and absence of display channel method faults are the useful signals.
