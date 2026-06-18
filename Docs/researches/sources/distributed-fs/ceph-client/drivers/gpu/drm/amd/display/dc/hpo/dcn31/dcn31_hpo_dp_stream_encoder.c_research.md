# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c

Purpose: Implements the DCN3.1 HPO DP stream encoder. It controls DP2 stream reset/enable, blank/unblank sequencing, MSA/pixel-format programming, secondary data packets, DSC PPS packets, stream-to-link mapping, audio, and readback.

Important APIs and functions: `dcn31_hpo_dp_stream_enc_enable_stream` resets and enables the 32-symbol encoder. `dp_unblank` selects pixel source, enables video and FIFOs, and enables CRC. `dp_blank` disables video/SDP/FIFOs with a vblank-sized wait. `set_stream_attribute` maps CRTC timing, pixel encoding, color depth, color space, compressed flag, and DP MISC bits into pixel-format and MSA registers. `update_dp_info_packets`, `stop_dp_info_packets`, and `set_dsc_pps_info_packet` program VPG generic packets and SDP controls. Audio setup/enable/disable delegates to APG and manages SDP audio bits.

Control flow: the stream encoder vtable sequences enable, attribute programming, mapping to link encoder, unblank, info packet/audio updates, and eventual blank/disable. DSC PPS packets are split into four generic packet slots starting at index 11, while VSC/SPD/HDR/adaptive-sync use fixed packet indices.

State and persistence: object state stores context, BIOS pointer, instance, engine id, VPG/APG pointers, and register metadata. Hardware state includes stream enable, MSA registers, SDP packet enables, FIFO state, mapper target, and audio packet flags.

Dependencies and integration: depends on `dcn31_hpo_dp_stream_encoder.h`, `reg_helper.h`, `dc.h`, VPG, APG, timing/color structures, and DP infoframe definitions. Integrated with DP link programming, DSC, adaptive sync, HDR metadata, and audio routing.

Risks and test signals: interlaced modes break to debugger. MSA packing is bit-sensitive and depends on 8-bit lane fields. SDP stream disable must consider audio/GSP state to avoid cutting active packets. Tests should cover timing-to-MSA vectors, RGB/YCbCr/420/Y-only color cases, compressed DSC PPS enable/disable, adaptive-sync line numbers, audio with/without APG clock field, and mapper bounds.
