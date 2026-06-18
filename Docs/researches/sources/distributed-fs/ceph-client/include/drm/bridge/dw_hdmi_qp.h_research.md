# sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi_qp.h

Purpose: platform contract for the newer DesignWare HDMI QP bridge, binding SoC PHY callbacks, IRQs, reference clock, color-format mask, and max bpc into the common HDMI QP implementation.

Important APIs/types/functions: `struct dw_hdmi_qp_phy_ops`, `struct dw_hdmi_qp_plat_data`, `dw_hdmi_qp_bind`, `dw_hdmi_qp_suspend`, and `dw_hdmi_qp_resume`.

Control flow: platform code passes encoder and platform data to `dw_hdmi_qp_bind`; the common bridge uses PHY init/disable/HPD callbacks, IRQ numbers, and ref clock data, while PM code calls suspend/resume helpers.

State and persistence: state is opaque in `struct dw_hdmi_qp`; hardware and PHY register state persists only while powered and must be restored on resume.

Dependencies and integration points: DRM encoders/connectors, platform devices, device PM, CEC IRQ routing, PHY glue, and HDMI color-format negotiation.

Risks and test signals: risks are wrong supported-format masks, bpc underdeclaration, IRQ/ref-clock mismatches, and PHY HPD setup ordering. Test bind failure paths, suspend/resume with a sink, CEC IRQs, HPD behavior, and 8/10/12-bpc modes.
