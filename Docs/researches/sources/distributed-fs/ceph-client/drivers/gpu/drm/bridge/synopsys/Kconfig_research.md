# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/synopsys/Kconfig

Purpose: defines Kconfig symbols for Synopsys DesignWare DRM bridge cores and their optional audio/CEC companion blocks.

Important APIs/types/functions: symbols include `DRM_DW_DP`, `DRM_DW_HDMI`, `DRM_DW_HDMI_AHB_AUDIO`, `DRM_DW_HDMI_I2S_AUDIO`, `DRM_DW_HDMI_GP_AUDIO`, `DRM_DW_HDMI_CEC`, `DRM_DW_HDMI_QP`, `DRM_DW_HDMI_QP_CEC`, `DRM_DW_MIPI_DSI`, and `DRM_DW_MIPI_DSI2`. The hidden core symbols select DRM display helpers, HDMI/DP helpers, KMS helpers, and `REGMAP_MMIO`; user-visible companion symbols depend on the core plus ALSA/ASoC/CEC prerequisites.

Control flow: this file influences build-time dependency selection only. Platform drivers select the hidden core symbols, then optional audio/CEC entries expose user choices when their sound/CEC dependencies are present.

State and persistence: no runtime state. The selected symbols persist in kernel configuration and determine which objects are built.

Dependencies and integration: integrates the Synopsys bridge objects with DRM helper libraries, ALSA PCM/IEC958/ELD, ASoC HDMI codec, CEC core/notifier, and regmap. `DRM_DW_HDMI_QP_CEC` is a bool tied to the QP HDMI bridge rather than a standalone module.

Risks: missing selects can produce link failures in platform drivers that expect helper APIs. Overly broad selects can pull CEC or audio support into configurations that do not need it. The help text has minor spelling issues and `DRM_DW_HDMI_CEC` says "CE interface", but behavior is unaffected.

Test signals: allmodconfig/allyesconfig builds, platform configs selecting each hidden core, modular builds for AHB/GP/I2S/CEC companions, and compile tests with CEC/SND/SND_SOC disabled.
