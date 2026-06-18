# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pvi.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pvi.c

## Purpose

This bridge controls the i.MX8MP HDMI TX Parallel Video Interface. It sits before the next HDMI bridge and configures LCDIF mode plus input/output sync and data-enable polarities.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi_pvi` stores bridge, device, and MMIO base. Key functions are `imx8mp_hdmi_pvi_probe/remove()`, `imx8mp_hdmi_pvi_bridge_attach()`, `imx8mp_hdmi_pvi_bridge_enable/disable()`, and `imx8mp_hdmi_pvi_bridge_get_input_bus_fmts()`.

## Control Flow

Probe maps registers, finds the downstream bridge from port 1, enables runtime PM, copies downstream timings, and adds the bridge. Attach attaches the downstream bridge. Atomic enable resumes runtime PM, obtains adjusted mode and bus flags, sets LCDIF mode/enabled, mirrors HS/VS polarity to input and output bits, applies DE-high if required, and writes control. Disable clears control and releases runtime PM. Input bus format negotiation delegates to the next bridge.

## State And Persistence Behavior

State is volatile MMIO and next-bridge reference. There is no cached mode. Runtime PM brackets active video interface programming.

## Dependencies And Integration Points

It depends on OF graph, DRM bridge chaining, runtime PM, and downstream bridge timing or atomic bus flags. It is part of the i.MX8MP HDMI TX pipeline with DW HDMI.

## Risks And Test Signals

Risks include NULL assumptions around connector/CRTC state in enable, failing if no downstream bridge is ready, and returning NULL bus formats when next bridge lacks negotiation. Test signals are correct HDMI image polarity, DE handling, runtime PM balance, and bridge-chain attach order.
