# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.h

Purpose: declares the DCE/DCE110 stream encoder private object, register lists, field shift/mask tables, and constructor/audio helper prototypes used by generation-specific AMD display resource code.

Important types and APIs: `struct dce110_stream_encoder` embeds `struct stream_encoder` and adds `regs`, `se_shift`, and `se_mask`. `struct dce110_stream_enc_registers` enumerates AFMT, HDMI, DP, DIG, DAC, MSA, and double-buffer control registers. `struct dce_stream_encoder_shift` and `struct dce_stream_encoder_mask` provide matching field metadata for `REG_UPDATE` macros. Public constructors are `dce110_stream_encoder_construct()` and `dce110_analog_stream_encoder_construct()`. Public audio helpers expose DP and HDMI audio setup/enable/disable/mute.

Control flow role: this header is not executable, but it shapes all register access in `dce_stream_encoder.c`. Resource constructors instantiate static register, shift, and mask tables using macros such as `SE_COMMON_REG_LIST()`, `SE_DCN_REG_LIST()`, and generation-specific `SE_COMMON_MASK_SH_LIST_*()` variants, then pass those tables into the constructor.

State and persistence: the header defines persistent per-instance state as table pointers, not owned register storage. Register addresses are immutable descriptors; actual state lives in hardware. Optional generation fields are represented as zero register addresses or zero masks, which implementation code uses for feature probing in selected paths.

Dependencies and integration: depends on `stream_encoder.h`, AMD register macro conventions (`SR`, `SRI`, field concatenation), `container_of`, DC audio types through prototypes, and engine identifiers. It bridges DCE8/10/11/12 and DCN10 naming differences by supplying alternate register and mask-list macros.

Risks: field-list drift is a major risk: implementation code assumes shift and mask structures contain every field it touches. Some register aliases differ between DCE and SOC/DCN naming, making macro selection important. Test signals are compile coverage across DCE80/100/110/112/120/DCN10 tables, successful construction for analog versus digital engines, and runtime validation that optional packet/update fields are zero-gated only where implementation checks them.
