# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_dual_mode_helper.h

Purpose: helper declarations and register definitions for DP++ dual-mode adapters and LSPCON level-shifter/protocol-converter devices accessed through DDC I2C.

Important APIs/types/functions: DP dual-mode register offsets for IDs, revisions, TMDS clock, I2C speed, TMDS output, CEC pin control, and LSPCON mode; `enum drm_lspcon_mode`, `enum drm_dp_dual_mode_type`, raw read/write helpers, adapter detect, max TMDS clock, TMDS output get/set, type name, and LSPCON get/set mode.

Control flow: drivers probe over DDC, classify the adapter, read TMDS limits, enable/disable TMDS output, and optionally switch LSPCON LS/PCON modes with timeout handling.

State and persistence: no header state. Adapter registers hold external dongle state while powered.

Dependencies and integration points: Linux types, DRM device context, I2C adapters, DP connectors, HDMI/DVI sinks, LSPCON HDMI 2.0 conversion, and CEC enablement.

Risks and test signals: unreliable DDC, ambiguous type1 DVI, TMDS limit misreads, LSPCON timeout, and CEC pin assumptions are risks. Test passive DP++ dongles, type2 HDMI, LSPCON switching, TMDS toggling, high TMDS validation, and failed/short I2C.
