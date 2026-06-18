# sources/distributed-fs/ceph-client/sound/soc/kirkwood/Makefile

## Purpose
Builds the Kirkwood/MVEBU audio controller module and the Armada 370 DB machine module.

## Important APIs, Types, And Functions
`snd-soc-kirkwood-y` combines `kirkwood-dma.o` and `kirkwood-i2s.o`; `snd-soc-armada-370-db-y` builds `armada-370-db.o`.

## Control Flow, State, And Persistence
This is build metadata only.

## Dependencies And Integration Points
Integrates with `CONFIG_SND_KIRKWOOD_SOC` and `CONFIG_SND_KIRKWOOD_SOC_ARMADA370_DB`.

## Risks And Test Signals
Risks are symbol/object mismatches. Test signals are module builds of both composite objects.
