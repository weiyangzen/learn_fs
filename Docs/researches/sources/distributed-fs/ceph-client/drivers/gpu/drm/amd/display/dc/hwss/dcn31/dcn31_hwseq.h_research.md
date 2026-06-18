# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn31/dcn31_hwseq.h

## Purpose
Declares DCN31 HWSS helpers for init, power gating, infoframes, Z10, HUBP PG, system context, reset, backlight, HPO, and static-screen control.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and declares functions implemented in `dcn31_hwseq.c`. It also declares `dcn31_is_abm_supported` and `dcn31_init_pipes`, which are not implemented in the read file and may be external/stale declarations.

## Control Flow
No executable flow.

## State and Persistence Behavior
No direct state. Declared functions mutate hardware and DC pipe/resource state.

## Dependencies and Integration Points
Consumed by DCN31 and DCN314 init tables. Provides later generation access to DCN31 reset, HPO, and power functions.

## Risks and Test Signals
Prototype/link consistency matters because some declarations were not present in this source. Build/link tests plus runtime coverage of HPO, Z10, PG, reset, and backlight hooks are important.
