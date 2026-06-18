# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn21/dcn21_hwseq.h

## Purpose
Declares DCN 2.1 HWSS helpers for system context, power optimization, platform workaround, ABM pipe setup, backlight, and ABM support detection.

## Important APIs, Types, and Functions
Includes `hw_sequencer_private.h`, forward-declares `struct dc`, and exposes all functions implemented in `dcn21_hwseq.c`.

## Control Flow
No executable flow. The prototypes are consumed by DCN21 and later-generation init tables.

## State and Persistence Behavior
No direct state; declared functions affect Hubbub, DMUB, clock, stream, ABM, and panel state.

## Dependencies and Integration Points
Connects `dcn21_init.c`, `dcn30_init.c`, `dcn301_init.c`, `dcn31_init.c`, and `dcn314_init.c` to common DCN21 behavior.

## Risks and Test Signals
Prototype stability is critical because multiple generations reuse these hooks. Compile coverage and backlight/power-state runtime tests are the key signals.
