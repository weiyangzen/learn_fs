# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.h

Purpose: This header defines the public DP link model consumed by DP controller, panel, and display orchestration code.

Important APIs and types: `struct msm_dp_link_info` stores DPCD revision, active rate, supported eDP rates, rate-set index, lane count, and enhanced framing capabilities. `struct msm_dp_link_test_video`, `struct msm_dp_link_test_audio`, and `struct msm_dp_link_phy_params` capture automated-test data. `struct msm_dp_link` aggregates LTTPR caps/count, sink request/response, sink count, test structs, link params, lane map, max lane count, and max link rate. `msm_dp_link_bit_depth_to_bpp()` converts DP test bit depth values to RGB bpp. Public functions cover request processing, colorimetry, level adjustment, PSM, test response/checksum, and object creation.

Control flow and state: The header’s state is populated by `dp_panel.c` during DPCD sink-cap reads, by `dp_link.c` during HPD IRQ parsing, and by `dp_ctrl.c` during link training. `sink_request` is the main handoff from AUX parsing to display/controller code.

Dependencies and integration: It includes `dp_aux.h` and DRM DP helper definitions. It is included by DP display, panel, and control layers, so it forms the common contract for negotiated link capabilities and compliance-test parameters.

Risks and test signals: Risks are mainly ABI-like within the driver: changing enum/field semantics can break link training or compliance tests. Test with all supported lane counts/rates, 6/8/10 bpc test patterns, PHY pattern requests, and lane-map programming in the controller.
