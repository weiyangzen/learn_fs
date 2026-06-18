# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.c

## Purpose
Implements the Tegra VIP parallel video bridge as a host1x client and V4L2 subdevice.

## Important APIs, Types, And Functions
Inline helpers convert host1x client/subdev/channel pointers. `tegra_vip_channel_get_prev_subdev()` finds the upstream subdevice connected to the VIP sink pad. Stream ops resume runtime PM, call SoC `vip_start_streaming()`, and then start the previous subdev; stream-off calls previous subdev stop and drops PM. DT parsing requires a parallel bus endpoint and exactly two pads. Channel init registers a media bridge subdev. Probe creates `struct tegra_vip`, attaches SoC data, registers as host1x client, and enables runtime PM.

## Control Flow
Platform probe registers the host1x client. Host1x init parses the VIP node and registers the subdevice. VI graph completion links VIP between upstream source and VI video node. During VI stream-on, VIP programs hardware and starts upstream streaming.

## State And Persistence
Runtime state is one `tegra_vip_channel` with subdev, pads, and DT node, plus device-level SoC/client pointers. No persistent storage.

## Dependencies And Integration Points
Depends on V4L2 fwnode/media/subdev, OF graph, runtime PM, host1x, and Tegra20 VIP SoC ops. Integrates with VI through media links and subdev hostdata set by graph completion.

## Risks And Test Signals
`prev_subdev` is assumed present in stream paths; malformed graphs can cause failures. Runtime PM is enabled after host1x registration in probe, so ordering should be checked. Test signals include parallel endpoint parsing, media link creation, stream-on/off with upstream decoder, and probe/remove cycles.
