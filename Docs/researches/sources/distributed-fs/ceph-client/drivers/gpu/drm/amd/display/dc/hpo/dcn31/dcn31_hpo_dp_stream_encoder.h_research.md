# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h

Purpose: Declares the DCN3.1 HPO DP stream encoder register schema, field masks, object layout, and constructor.

Important APIs and types: `struct dcn31_hpo_dp_stream_encoder` embeds `hpo_dp_stream_encoder` and stores register/shift/mask pointers. Register-list macros enumerate stream mapper, clock, input mux, audio, FIFO, SYM32 video, MSA, SDP, CRC, and HBLANK registers. Custom MSA lane field shift/mask definitions make generic `REG_SET_4` packing possible. DCN4.2 APG clock field macros extend the same struct.

Control flow: resource code expands macros into static register/field tables and calls `dcn31_hpo_dp_stream_encoder_construct`. Runtime code accesses operations through `hpo_dp_stream_encoder_funcs`.

State and persistence: struct state is mostly references to hardware metadata and owned base fields. The header itself defines no synchronization or persistence.

Dependencies and integration: includes DCN30 VPG, DCN31 APG, and `stream_encoder.h`. It bridges stream encoder core code with generation-specific packet/audio blocks.

Risks and test signals: incorrect macro expansion affects all stream operations. Compile tests should cover DCN31 and DCN42 field sets, and runtime readback should verify mapper, pixel format, SDP, and MSA registers after programming.
