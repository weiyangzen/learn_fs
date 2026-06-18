<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c

## Purpose
`adv748x-csi2.c` implements TXA/TXB CSI-2 transmitter V4L2 subdevices for ADV748x. It models a sink/source bridge, registers internal links from HDMI/AFE sources, propagates formats, exposes pixel-rate control, reports CSI-2 bus configuration, and delegates stream enablement to the selected upstream source.

## Important APIs, Types, and Functions
- `adv748x_csi2_set_virtual_channel()` writes the CSI virtual-channel register.
- `adv748x_csi2_register_link()` registers source subdevices as needed and creates internal media links.
- `adv748x_csi2_registered()` builds default links: HDMI to TXA enabled by default, AFE to TXB enabled by default when present, and AFE to TXA available.
- `adv748x_csi2_s_stream()` finds the remote sink source and calls its `s_stream`.
- Pad ops enumerate supported bus codes: TXA supports UYVY16 and RGB888; TXB supports UYVY16 only.
- `adv748x_csi2_set_pixelrate()` updates the read-only-style pixel-rate control from upstream format logic.

## Control Flow
Init skips disabled TX ports, initializes the subdevice and internal ops, creates sink/source pads, binds the OF endpoint for async registration, initializes controls, finalizes subdev state with the parent mutex, and async-registers. Once the TX subdevice is registered into a V4L2 device, its registered callback creates internal links to AFE/HDMI. Stream calls flow backward from TX to source subdev, where HDMI/AFE powers the transmitter.

## State and Persistence
Each `struct adv748x_csi2` tracks page, port, configured lane count, active lane count, current source pointer, pixel-rate control, and pad state. Format state is V4L2 subdev active/try state, protected by the parent mutex. Link setup in core mutates `src` and `active_lanes`.

## Dependencies and Integration Points
It depends on parent state/helpers, media entity links, V4L2 async subdev endpoint matching, and upstream HDMI/AFE subdevices. It is the externally registered endpoint for capture drivers consuming MIPI CSI-2.

## Risks
- Streaming without an enabled media link returns `-EPIPE`.
- Pixel-rate control accepts only updates through helper; direct `s_ctrl` is a no-op for valid ID.
- Format propagation is local to TX pads and does not validate remote source compatibility beyond link validation.
- TXA/TXB support different bus codes, so graph negotiation must avoid RGB888 on TXB.

## Test Signals
Test TXA/TXB registration with enabled and disabled endpoints, default link topology, media link switching, stream delegation error when unlinked, format enumeration and fallback for unsupported codes, source-pad format mirroring, `get_mbus_config` lane counts after AFE-to-TXA active-lane reduction, and pixel-rate updates from HDMI/AFE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-csi2.c -->
