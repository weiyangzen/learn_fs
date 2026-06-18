# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_common.c

Purpose: Implements shared HDMI helper functions for PHY lane parsing from device tree and HDMI Audio Clock Regeneration N/CTS calculation.

Important APIs/functions: `hdmi_parse_lanes_of()` reads an optional 8-entry `lanes` property from an OF graph endpoint, validates its length, and delegates to `hdmi_phy_parse_lanes()`. If absent, it applies the default ordered lane map `{0,1,2,3,4,5,6,7}`. `hdmi_compute_acr()` accepts pixel clock and audio sample frequency, selects HDMI-spec N values, applies limited deep-color corrections when applicable, and computes CTS.

Control flow: HDMI4/HDMI5 probe code calls lane parsing after locating the output endpoint. Audio configuration calls ACR calculation after deriving the sample rate from IEC958 channel status. Unsupported sample rates or null output pointers return `-EINVAL`.

State and persistence: No state persists here. Lane results are stored in caller-owned `struct hdmi_phy_data`; ACR results are written through caller pointers.

Dependencies/integration: Uses OF property helpers, OMAP HDMI common headers, HDMI PHY parsing, and kernel division helpers. It supports both HDMI4 and HDMI5 top-level drivers.

Risks and test signals: `hdmi_compute_acr()` currently hardcodes deep color to 100 percent, so deep-color modes are not truly represented. Lane parsing requires exactly four differential pairs encoded as eight cells. Validate DT lane remap/polarity variants, missing lane defaults, invalid lane arrays, and all supported audio sample rates from 32 kHz to 192 kHz.
