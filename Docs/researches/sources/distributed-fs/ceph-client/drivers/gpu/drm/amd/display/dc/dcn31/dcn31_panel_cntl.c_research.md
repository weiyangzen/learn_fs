# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_panel_cntl.c

Purpose: Implements DCN31 panel control through DMUB commands rather than direct PWM register programming.

Important APIs/types/functions: `dcn31_panel_cntl_construct()` installs `panel_cntl_funcs` and maps the panel to a power sequencer instance. `dcn31_query_backlight_info()` sends `DMUB_CMD__PANEL_CNTL_QUERY_BACKLIGHT_INFO`. `dcn31_panel_cntl_hw_init()` sends `DMUB_CMD__PANEL_CNTL_HW_INIT` and optionally `DMUB_CMD__PANEL_DEBUG_PWM_FREQ`.

Control flow: Query helpers zero a `union dmub_rb_cmd`, fill header type/subtype/payload size and `pwrseq_inst`, then call `dc_wake_and_execute_dmub_cmd(...WAIT_WITH_REPLY)`. Hardware init passes cached PWM/ref-divider values to DMUB, stores returned values back into `stored_backlight_registers`, optionally sends debug PWM frequency if within `200..6250 Hz`, then returns current backlight. Constructor maps power sequencer by DIG engine when `support_edp0_on_dp1` is set; otherwise it uses the panel instance.

State/persistence: Persistent state is the base panel controller, `pwrseq_inst`, and cached backlight registers returned by DMUB. Hardware details are owned by DMUB firmware.

Dependencies/integration: Depends on `dc_dmub_srv`, DMUB command formats, panel controller abstraction, and DC config/debug fields.

Risks: If `dmub_srv` is absent or a command fails, APIs return `0` or `false`, which is indistinguishable from valid off/zero backlight to some callers. Unsupported engine ids assert and log but leave `pwrseq_inst` as `0xF`.

Test signals: Mock DMUB replies for init/query paths, test debug frequency bounds, verify pwrseq mapping for DIGA/DIGB and legacy mode, and failure handling when DMUB is unavailable.
