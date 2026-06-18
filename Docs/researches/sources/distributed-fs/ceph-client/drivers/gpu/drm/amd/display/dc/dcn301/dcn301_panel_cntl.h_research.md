# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn301/dcn301_panel_cntl.h

Purpose: Declares the DCN301 direct-register panel controller type and its register/field metadata.

Important APIs/types/functions: `DCN301_PANEL_CNTL_REG_LIST()` maps power sequencer and PWM registers. `DCN301_PANEL_CNTL_MASK_SH_LIST()` and `DCN301_PANEL_CNTL_REG_FIELD_LIST()` enumerate panel power, PWM duty, fractional enable, register lock, update pending, and reference divider fields. `struct dcn301_panel_cntl` embeds `struct panel_cntl` and stores register, shift, and mask tables.

Control flow: Header-only declarations; construction and function dispatch are implemented in the C file.

State/persistence: The structure keeps metadata pointers; mutable backlight cache is inherited from `struct panel_cntl`.

Dependencies/integration: Includes `panel_cntl.h` and `dce/dce_panel_cntl.h`, tying DCN301 to the generic panel controller abstraction and DCE-era register naming.

Risks: Field-list order must match generated shift/mask initializers. The register list assumes `id`-indexed panel/PWM instances; wrong resource wiring would direct backlight writes to the wrong hardware block.

Test signals: Compile-time expansion in DCN301 resource code and direct-register backlight tests that use every field declared here.
