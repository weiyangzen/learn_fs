# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.h

## Purpose
Declares the Tegra VIP parallel-input bridge structures and SoC operation interface.

## Important APIs, Types, And Functions
Pad constants define sink/source layout. `struct tegra_vip_channel` owns the subdev, two media pads, and DT node. `struct tegra_vip_ops` currently has `vip_start_streaming()`. `struct tegra_vip_soc` wraps ops. `struct tegra_vip` owns device, host1x client, SoC data, and the single channel. Tegra20/Tegra30 builds export `tegra20_vip_soc`.

## Control Flow
The generic VIP implementation calls SoC start-streaming through this interface while VI controls the overall pipeline.

## State And Persistence
Runtime-only state; media graph registration persists only while the device is bound.

## Dependencies And Integration Points
Depends on V4L2 async/subdev and media entities. Integrated by `vip.c`, `tegra20.c`, and top-level platform driver registration.

## Risks And Test Signals
The current ops interface lacks stop/error callbacks, so any hardware needing explicit disable would need extension. Test signals include compile coverage for non-Tegra20 builds and stream cycles on VIP hardware.
