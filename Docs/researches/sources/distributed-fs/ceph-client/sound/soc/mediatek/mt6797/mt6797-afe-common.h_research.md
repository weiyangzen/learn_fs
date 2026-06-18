# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt6797/mt6797-afe-common.h

## Purpose

This common header defines MT6797 memif IDs, DAI IDs, IRQ IDs, platform-private clock state, sample-rate transform declarations, and sub-DAI registration entry points.

## Important APIs, Types, and Functions

Memif enum covers DL1/DL2/DL3, VUL/AWB/VUL12, DAI, MOD_DAI, then DAI IDs for ADDA, PCM1, PCM2, hostless loopback, and hostless speech. IRQ enum exposes IRQ1/2/3/4/7. `struct mt6797_afe_private` stores a dynamically allocated clock pointer array. The header declares `mt6797_general_rate_transform()`, `mt6797_rate_transform()`, and three DAI registration callbacks.

## Control Flow

The platform probe uses the registration callbacks to build `afe->sub_dais`, then combines them into one DAI component. Rate-transform helpers are used by FE/IRQ setup and by DAI-specific `hw_params`.

## State and Persistence Behavior

Only the clock pointer array is defined as private state here. Memif/IRQ/DAI state is stored in common `mtk_base_afe` arrays initialized by the platform file.

## Dependencies and Integration Points

Includes ALSA SoC, Linux list/regmap, and common MediaTek base AFE infrastructure. It is shared by all MT6797 platform and sub-DAI files.

## Risks and Edge Cases

Enum ordering is critical because array indexes and DAI IDs depend on it. `MT6797_DAI_ADDA = MT6797_MEMIF_NUM` means adding memifs shifts all DAI IDs unless all users are updated.

## Test Signals

Compile all MT6797 objects and inspect registered DAI names/IDs. Stream tests on every memif and DAI validate ID alignment.
