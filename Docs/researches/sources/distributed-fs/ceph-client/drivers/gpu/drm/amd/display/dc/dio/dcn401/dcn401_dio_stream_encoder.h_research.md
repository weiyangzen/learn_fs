# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn401/dcn401_dio_stream_encoder.h

## Purpose
Declares the DCN401 stream encoder register field list and public constructor/helper prototypes. It is the contract between DCN401 resource construction, generated register tables, and the implementation in `dcn401_dio_stream_encoder.c`.

## Important APIs, Types, And Functions
The key macro is `SE_COMMON_MASK_SH_LIST_DCN401(mask_sh)`, a long field list consumed by register table generation for DP, HDMI, DIG, DME, FIFO, stream mapping, generic packets, DSC PPS/VBID, audio, and metadata registers. The header declares `dcn401_dio_stream_encoder_construct()` plus externally reused helpers such as `enc401_set_dynamic_metadata()`, `enc401_stream_encoder_set_stream_attribute_helper()`, DP/DVI/HDMI stream attribute functions, `enc401_stream_encoder_dp_unblank()`, `enc401_stream_encoder_enable()`, `enc401_set_dig_input_mode()`, `enc401_stream_encoder_map_to_link()`, and `enc401_read_state()`.

## Control Flow
The header has no runtime control flow. Its macro expands into register shift/mask initializers, and its prototypes allow DCN42 and resource code to reuse DCN401 implementation pieces. The implementation flow is controlled by the `stream_encoder_funcs` table installed by the constructor.

## State And Persistence
No runtime state is stored here. The macro defines compile-time access to hardware register fields, and the prototypes describe functions that mutate stream encoder object fields or hardware registers in the C file.

## Dependencies And Integration Points
The header includes DCN30 VPG/AFMT definitions, `stream_encoder.h`, and DCN20 stream encoder definitions. DCN42 stream encoder code includes this header to reuse DCN401 DP/DVI, unblank, dynamic metadata, enable, input-mode, map-to-link, and state read functions.

## Risks
Because the mask/shift list is broad, missing or misnamed fields break compilation or cause incorrect register programming if generated register tables drift from hardware specs. The list mixes DIG0 and DIG1 HDMI fields for TMDS pixel/color format, so platform register naming must match exactly. Public helper reuse by newer ASICs increases compatibility risk when a DCN401 register field changes semantics.

## Test Signals
Build-time validation is the primary signal: register field macros must resolve and function prototypes must match call sites. Runtime signals come indirectly from mode-set paths using DCN401/DCN42 stream encoders, especially DP DSC, generic packets, HDMI metadata/audio, DIG FIFO, and stream-to-link mapping.
