<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c

## Purpose
This file provides the GK104/GK110 base channel constructor with an expanded supported primary-plane format list while reusing the NV907C method implementation.

## Important APIs, Types, and Functions
It defines `base917c_format` and `base917c_new`.

## Control Flow
The constructor delegates to `base507c_new_` with the exported `base907c` function table, the GK-era format list, and the class-specific interlock bit layout.

## State and Persistence Behavior
No separate state is introduced. Base channel state is managed by the reused `base907c` methods and common window/channel objects.

## Dependencies and Integration Points
It depends on `base907c`, DRM format constants, and `base507c_new_`. `base.c` selects this constructor for GK104/GK110 and newer pre-GV100 base-channel classes listed there.

## Risks
New formats such as XRGB/ARGB2101010 are exposed only if the reused NV907C method encodings support them. Any class difference not covered by the shared function table would surface as incorrect display programming.

## Test Signals
Primary plane commits for every listed format on GK-class hardware, especially RGB/BGR 10-bit and FP16 formats, plus LUT/CSC behavior inherited from NV907C are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/base917c.c -->
