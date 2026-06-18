# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.c

Purpose: Implements DCN31 AFMT object construction and memory low-power control while reusing DCN30 AFMT audio setup functions.

Important APIs/types/functions: `afmt31_construct()` binds a `struct dcn31_afmt` to context, instance, register tables, and `dcn31_afmt_funcs`. `afmt31_powerdown()` and `afmt31_poweron()` program `AFMT_MEM_PWR`. The function table delegates HDMI/DP audio setup, mute, and audio info updates to `afmt3_*` routines.

Control flow: Powerdown returns immediately unless `debug.enable_mem_low_power.bits.afmt` is set, then clears `AFMT_MEM_PWR_DIS` and forces memory low power. Poweron also honors the debug flag and writes the inverse force/disable values.

State/persistence: Software state is just object metadata. Hardware state is AFMT memory power force/disable bits plus the inherited AFMT audio registers programmed by delegated functions.

Dependencies/integration: Includes DCN30 AFMT helpers, `dc/dc.h` debug flags, and register helpers. Stream encoder HDMI/DP audio paths can call AFMT power hooks through `enc->afmt`.

Risks: Low-power behavior is gated by a debug bit, so tests must cover both enabled and disabled paths. Incorrect polarity on `AFMT_MEM_PWR_DIS`/`AFMT_MEM_PWR_FORCE` would cause audio formatting memory to remain powered down or never enter low power.

Test signals: Register tests should confirm no writes when AFMT low power is disabled, and correct `AFMT_MEM_PWR` writes during HDMI audio disable or display idle transitions.
