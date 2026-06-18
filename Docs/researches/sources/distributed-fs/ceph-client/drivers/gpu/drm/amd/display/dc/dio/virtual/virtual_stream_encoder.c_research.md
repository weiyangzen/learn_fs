# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/virtual/virtual_stream_encoder.c

## Purpose
Implements a virtual stream encoder for virtual display paths. It provides a complete `stream_encoder_funcs` table whose operations intentionally do nothing, allowing Display Core to use normal stream encoder call paths without touching hardware.

## Important APIs, Types, And Functions
`virtual_stream_encoder_construct()` validates the object and BIOS pointer, installs `virtual_str_enc_funcs`, and sets context, virtual engine id, and BIOS pointer. `virtual_stream_encoder_create()` allocates a zeroed encoder, constructs it, and frees it on failure. The function table covers DP/HDMI/DVI stream attributes, VCP throttling, HDMI/DP info packets, DP blank/unblank, audio mute, AVMUTE, OTG connect, stereo sync, ODM combine, HDMI reset, and DSC PPS packet programming.

## Control Flow
Every hardware-facing callback discards its arguments and returns immediately. Construction returns false for a null encoder or BIOS pointer. Creation returns null on allocation or construction failure, breaking to debugger before freeing a failed allocation.

## State And Persistence
The only persistent state is the allocated `stream_encoder` object with function table, context, `ENGINE_ID_VIRTUAL`, and BIOS pointer. No register, packet, audio, or timing state is changed.

## Dependencies And Integration Points
The file includes `dm_services.h` for allocation/assert support and `virtual_stream_encoder.h`. It is used by resource creation for virtual streams (`dc_resource.c`) and supports higher-level mode-set paths that expect a stream encoder object even for non-physical output.

## Risks
No-op behavior is correct only for virtual targets. If used accidentally with a physical stream, mode setting would appear to succeed while no hardware is programmed. The constructor requires a BIOS pointer even though callbacks do not use it, which can reject otherwise usable test contexts. The create path depends on `kzalloc_obj`, `BREAK_TO_DEBUGGER`, and `kfree` availability.

## Test Signals
Virtual stream creation should allocate and construct successfully with a valid BIOS pointer, physical register access should not occur, mode-set paths should tolerate all no-op callbacks, and allocation-failure tests should return null without leaks.
