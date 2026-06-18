# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h

Purpose: Declares the DCN31 AFMT hardware wrapper, register list, field metadata, power hooks, and constructor.

Important APIs/types/functions: `DCN31_AFMT_FROM_AFMT()` casts the base `struct afmt`. `AFMT_DCN31_REG_LIST()` adds AFMT audio/infoframe/channel-status registers and `AFMT_MEM_PWR`. `DCN31_AFMT_MASK_SH_LIST()` and `AFMT_DCN31_REG_FIELD_LIST()` cover audio source, channel enable, IEC 60958 channel status, sample send, and memory power fields. `struct dcn31_afmt` embeds `struct afmt`.

Control flow: Header-only declarations; dispatch is through `struct afmt_funcs` set in the C file.

State/persistence: Stores immutable register/shift/mask pointers and base context/instance.

Dependencies/integration: Consumed by DCN31 resource construction and by stream/audio encoder paths that need AFMT power control.

Risks: Register-field macro coverage must include all fields used by delegated DCN30 AFMT helpers, not just fields touched in `dcn31_afmt.c`. Missing `AFMT_MEM_PWR_STATE` support can limit diagnostics.

Test signals: Build with DCN31 resources and AFMT audio smoke tests for HDMI/DP channel status and memory low-power fields.
