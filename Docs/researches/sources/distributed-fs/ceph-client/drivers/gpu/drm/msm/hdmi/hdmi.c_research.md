# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/hdmi/hdmi.c

Purpose: top-level MSM HDMI transmitter platform driver. It owns HDMI device allocation, resource acquisition, component binding to MSM KMS, runtime PM of core power resources, IRQ fan-out, bridge/connector creation, PHY lookup, and module register/unregister plumbing.

Important APIs and functions:
- `msm_hdmi_set_mode()` writes `REG_HDMI_CTRL` under `reg_lock`, handling HDMI versus DVI mode and enable state.
- `msm_hdmi_irq()` dispatches a shared interrupt to HPD, DDC/I2C, and optional HDCP handlers.
- `msm_hdmi_init()` creates the workqueue, DDC adapter, and optional HDCP controller.
- `msm_hdmi_modeset_init()` creates the DRM bridge, optional next bridge, bridge connector, connector/encoder link, and IRQ request.
- `msm_hdmi_dev_probe()` maps MMIO/QFPROM, gets IRQ, regulators, clocks, optional external pixel clock, optional HPD GPIO, and associated PHY.
- runtime PM hooks enable/disable regulators, pinctrl state, and power clocks.

Control flow: platform probe collects all resources that may defer, finds the PHY through the `phys` phandle, enables runtime PM, and registers as a component. Component bind calls `msm_hdmi_init()` and stores `priv->kms->hdmi`. Later KMS calls `msm_hdmi_modeset_init()` to build DRM objects. Unbind/destroy tears down workqueue, HDCP, and DDC; remove unregisters the component and drops the PHY device reference.

State and persistence: `struct hdmi` persists audio state, booleans `power_on` and `hpd_enabled`, pixel clock, MMIO physical address for HDCP, regulator/clock handles, PHY pointer/device reference, DDC adapter, connector/bridge/encoder pointers, IRQ, workqueue, HDCP control, and `reg_lock`. `state_mutex` protects power/hpd booleans while `reg_lock` protects shared registers.

Dependencies and integration points: integrates with DRM bridge connector helpers, `drm_of_find_panel_or_bridge`, OF platform PHY lookup, Linux component framework, runtime PM, pinctrl, GPIO descriptors, regulators, clocks, MSM KMS private data, HDMI PHY driver registration, DDC and HDCP submodules, and compatible-specific power config tables.

Risks: `msm_hdmi_set_mode()` dereferences `hdmi->connector`, so call ordering must ensure connector exists. Runtime resume error path disables regulator and pinctrl but does not explicitly undo a partially enabled clock if `clk_bulk_prepare_enable()` fails internally after enabling some clocks, relying on bulk helper semantics. Optional QFPROM can be NULL, so HDCP users must tolerate it. IRQ handler assumes bridge and i2c are initialized by modeset setup.

Test signals: probe deferral when PHY, regulators, clocks, GPIO, or DDC are unavailable; component bind/unbind cycles; HDMI and DVI sink mode toggles; IRQ dispatch for HPD/DDC/HDCP; runtime PM suspend/resume; bridge connector creation with and without next bridge; and DT compatibility coverage for 8660/8960 and 8974-family configs.
