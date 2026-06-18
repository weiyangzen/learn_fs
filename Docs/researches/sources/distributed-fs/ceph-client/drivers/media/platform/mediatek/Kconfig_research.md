# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/Kconfig

## Purpose
This Kconfig file provides the MediaTek media platform driver menu and includes the sub-Kconfig files for the MediaTek JPEG, MDP, video codec, VPU, and MDP3 driver families.

## Important APIs, Types, And Functions
There are no C APIs. The file emits a menu comment and sources `drivers/media/platform/mediatek/jpeg/Kconfig`, `mdp/Kconfig`, `vcodec/Kconfig`, `vpu/Kconfig`, and `mdp3/Kconfig`.

## Control Flow And State
Kconfig inclusion order makes the nested MediaTek driver symbols visible under the media platform hierarchy. The state is entirely build-time configuration.

## Dependencies And Integration Points
This file is included by the parent media platform Kconfig. The adjacent Makefile mirrors this structure by descending into the same subdirectories. For this work item, the relevant child is `jpeg/Kconfig`, which defines `VIDEO_MEDIATEK_JPEG`.

## Risks
Path drift is the primary risk: if a subdirectory is renamed or removed, this Kconfig will break menu parsing. Inclusion order can matter if child symbols depend on symbols defined by earlier child files, so reordering should be deliberate.

## Test Signals
Run Kconfig parsing through normal kernel configuration targets and ensure all sourced child Kconfigs exist. Enable each child family independently to verify menu visibility and dependency reporting.
