# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/Kconfig

Purpose: declares Kconfig options for DRM display helper infrastructure, including bridge connectors, DP AUX bus/chardev/CEC/helper support, DP tunnels, DSC, HDCP, HDMI audio/CEC/notifier/helper/state helpers.

Important symbols: `DRM_DISPLAY_DP_AUX_BUS` builds the OF-backed DP AUX endpoint bus. `DRM_DISPLAY_HELPER` is the umbrella tristate and selects CEC core when DP AUX CEC, HDMI CEC, or CEC notifier support is enabled. Inside the helper block, `DRM_BRIDGE_CONNECTOR` selects HDMI audio/CEC/state helpers for connector termination of bridge chains. `DRM_DISPLAY_DP_AUX_CEC` enables CEC tunneling over DP AUX. `DRM_DISPLAY_DP_AUX_CHARDEV` enables `/dev/drm_dp_auxN`. `DRM_DISPLAY_DP_HELPER`, `DRM_DISPLAY_DP_TUNNEL`, `DRM_DISPLAY_DSC_HELPER`, `DRM_DISPLAY_HDCP_HELPER`, `DRM_DISPLAY_HDMI_*` symbols control helper object compilation.

Control flow: symbols select object lists in `display/Makefile` and expose helper APIs to DRM drivers.

State and persistence: Kconfig state persists in `.config`; runtime state is in individual helper modules/files.

Dependencies and integration points: connects DRM core to DisplayPort, HDMI, bridge connector, CEC, HDCP, DSC, and tunnel helper code. `DRM_DISPLAY_DP_AUX_BUS` additionally requires OF.

Risks: helper options are interdependent; missing selects can lead to bridge connectors without needed HDMI/CEC/audio functionality. `DRM_DISPLAY_DP_TUNNEL_STATE_DEBUG` requires debug/ref-tracker dependencies and should stay expert-only.

Test signals: all helper combinations compile, selected symbols pull expected objects, bridge connector HDMI/audio/CEC features link, and DP AUX char device/bus options can be built as intended.
