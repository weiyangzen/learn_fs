# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/hdmirx/Kconfig

## Purpose
Defines build-time configuration for the Synopsys DesignWare HDMI Receiver driver and its optional default EDID preload feature.

## Important APIs, Types, And Functions
The `VIDEO_SYNOPSYS_HDMIRX` tristate enables the HDMI 2.0 receiver module named `synopsys_hdmirx`. It depends on Rockchip architecture support or compile-test coverage and `VIDEO_DEV`, and selects media-controller, V4L2 subdev, contiguous vb2 DMA, CEC core, and HDMI helpers. `VIDEO_SYNOPSYS_HDMIRX_LOAD_DEFAULT_EDID` is a bool that preloads a Linux Foundation-branded EDID for out-of-box testing.

## Control Flow
Kconfig selection controls whether `snps_hdmirx.c` and `snps_hdmirx_cec.c` are compiled through the local Makefile. The default EDID option changes runtime behavior in `hdmirx_load_default_edid()`, where the driver either keeps HPD low until userspace programs EDID or writes the built-in EDID and raises HPD.

## State And Persistence
No runtime state exists in this file. Build configuration persists through the kernel `.config`; the EDID option affects initial in-kernel device state at probe.

## Dependencies And Integration Points
Integrates the driver with Linux media, vb2 DMA, CEC, HDMI infoframe/EDID helpers, and Rockchip-oriented platform support. The optional EDID knob is explicitly suitable for non-production setups.

## Risks
Enabling the default EDID in a product can expose generic identity and limited modes instead of board/vendor-specific EDID. Disabling it leaves the device mostly unusable until userspace sets EDID, which is intentional but can look like a probe/runtime failure during bring-up.

## Test Signals
Build matrix coverage should verify builtin and module configurations, with and without default EDID. Runtime smoke tests should confirm HPD behavior and `v4l2-ctl --get-edid` after probe.
