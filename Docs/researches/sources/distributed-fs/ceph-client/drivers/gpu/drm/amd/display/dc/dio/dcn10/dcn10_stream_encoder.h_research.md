# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h

Purpose: Declares the DCN10 stream encoder register model, field macro lists shared by later generations, concrete object type, and public stream encoder helpers.

Important APIs/types/functions: `SE_COMMON_DCN_REG_LIST()` and `struct dcn10_stream_enc_registers` cover AFMT, HDMI, DP MSA, DP secondary-packet, DSC/metadata, DIG FIFO/clock, and audio registers. Field lists span DCN1.0 through DCN4.01 and audio-common extensions. Prototypes cover construction, DP/HDMI/DVI setup, packet updates, blank/unblank, audio, DIG routing, HDMI reset, audio clock lookup, and DP pixel format readback.

Control flow: Header-only; function dispatch occurs through `struct stream_encoder_funcs` in C files.

State/persistence: `struct dcn10_stream_encoder` embeds the base stream encoder and stores register/shift/mask metadata. Runtime hardware state is external to the struct.

Dependencies/integration: Includes `stream_encoder.h`; reused by DCN20 stream encoder and newer modules via common register/field lists.

Risks: This is a cross-generation macro surface; field-list drift can break unrelated generations. Register structs include fields not present on every generation, so resource code must provide correct zero or real addresses.

Test signals: Cross-generation build coverage, resource-table initialization, and function-table users compiling against all declared helper prototypes.
