# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.h

Purpose: Declares the DCN31 DMUB-backed panel controller.

Important APIs/types/functions: Defines debug PWM frequency bounds `MIN_DEBUG_FREQ_HZ` and `MAX_DEBUG_FREQ_HZ`, `struct dcn31_panel_cntl` embedding `struct panel_cntl`, and `dcn31_panel_cntl_construct()`.

Control flow: None in the header; all behavior is through the function table set by the constructor.

State/persistence: No DCN31-specific fields beyond the inherited base; `pwrseq_inst` and cached backlight registers live in `struct panel_cntl`.

Dependencies/integration: Includes `panel_cntl.h` and `dce/dce_panel_cntl.h` so it can reuse common panel storage while delegating hardware operations to DMUB in the C file.

Risks: Because this structure has no register table, any caller expecting DCN301-style direct register access would be incompatible. Frequency bounds must stay aligned with firmware expectations.

Test signals: Build-time constructor references and runtime tests for DMUB command population using inherited panel fields.
