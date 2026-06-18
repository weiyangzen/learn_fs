# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Makefile

## Purpose
Defines the object composition for the Tegra staging video input module.

## Important APIs, Types, And Functions
`tegra-video-objs` always includes `video.o`, `vi.o`, `vip.o`, and `csi.o`. SoC-specific objects add `tegra20.o` for Tegra2x/3x and `tegra210.o` for Tegra210. `obj-$(CONFIG_VIDEO_TEGRA)` links the module.

## Control Flow
The build graph determines which exported SoC data symbols exist for `of_match_table` entries in VI/CSI/VIP probe paths.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates with Kconfig architecture symbols and the platform drivers declared in `video.h`.

## Risks And Test Signals
Mismatched object inclusion can leave compatible table references unresolved or omit SoC ops. Test signals are per-architecture builds and module load symbol resolution.
