# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.h

## Purpose
Declares MediaTek SOF integration structures and helper functions for machine drivers.

## Important APIs, Types, And Functions
`struct sof_conn_stream` maps normal links to SOF links, SOF DMA widget names, and stream direction. `struct mtk_dai_link` stores saved BE fixups in a list. `struct mtk_sof_priv` supplies connection streams and optional SOF fixup callback. The header declares card probe, late probe, fixup, and DT DAI-link parse helpers.

## Control Flow, State, And Persistence
No direct control flow. The structures become persistent card-private metadata while SOF routes and fixups are active.

## Dependencies And Integration Points
Includes ASoC and is used by MediaTek machine drivers plus `mtk-soundcard-driver.c`.

## Risks And Test Signals
Risks include name-string ABI dependence and list ownership assumptions for saved fixups. Test signals are compile coverage and SOF/non-SOF machine probe tests.
