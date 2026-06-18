# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/ipuv3/dw_hdmi-imx.c

## Purpose
Provides the i.MX6-specific wrapper around the Synopsys DesignWare HDMI bridge. It supplies PHY/MPLL/current configuration tables, mode validation limits, i.MX GPR mux programming, and an encoder component that connects the generic HDMI bridge to the IPUv3 DRM device.

## Important APIs, types, and functions
- `struct imx_hdmi` stores device, regmap, generic `dw_hdmi` handle, and bridge pointer.
- `struct imx_hdmi_encoder` embeds the DRM encoder and links back to `imx_hdmi`.
- `dw_hdmi_imx_encoder_enable()` writes the HDMI mux selection into `IOMUXC_GPR3`.
- `dw_hdmi_imx_atomic_check()` sets `imx_crtc_state` bus format to RGB888 and DI hsync/vsync pins to 2/3.
- `imx6q_hdmi_mode_valid()` and `imx6dl_hdmi_mode_valid()` enforce 13.5 MHz to 216 MHz pixel-clock limits.
- `dw_hdmi_imx_probe()`, `dw_hdmi_imx_bind()`, and `dw_hdmi_imx_remove()` implement platform/component lifecycle.

## Control flow
Probe allocates private state, obtains the IOMUXC GPR syscon regmap from the `gpr` phandle, probes the generic DesignWare HDMI core with SoC-specific platform data, finds the DRM bridge from device tree, and registers as an i.MX DRM component. Bind allocates a TMDS encoder, parses possible CRTCs from the encoder's OF node, installs helper callbacks, and attaches the generic HDMI bridge. Encoder enable determines the active input port and programs the SoC HDMI mux.

## State and persistence
Runtime state persists in `struct imx_hdmi` and in the generic `dw_hdmi` instance. The selected HDMI input mux persists in IOMUXC GPR registers until changed. CRTC bus format/pin state is propagated per atomic check through `struct imx_crtc_state`.

## Dependencies and integration points
Depends on the generic `dw_hdmi` bridge driver, syscon/regmap for `fsl,imx6q-iomuxc-gpr`, DRM component binding, OF CRTC parsing, and IPUv3 CRTC state from `imx-drm.h`. It is one optional component of the `imx-display-subsystem` master.

## Risks
The wrapper caps modes at 216 MHz despite comments that hardware could go higher with missing setup data. Probe must correctly unwind both the bridge reference and `dw_hdmi` instance on component registration failure. GPR mux programming depends on device-tree port numbering and may silently choose the wrong IPU DI if graph data is wrong.

## Test signals
Validation includes probe deferral until the DW-HDMI bridge and IPUv3 CRTC exist, HDMI modes below/above the clock limits, correct DI-to-HDMI mux selection for both IPUs, EDID-driven connector creation through the bridge, and cleanup on module removal.
