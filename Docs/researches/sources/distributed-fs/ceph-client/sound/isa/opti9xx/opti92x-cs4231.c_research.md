# sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-cs4231.c

## Purpose
`opti92x-cs4231.c` is a wrapper build unit for OPTi 82C92x cards using CS4231/CS4248-compatible codec behavior. It defines `CS4231` and includes `opti92x-ad1848.c`.

## Important APIs, Types, and Functions
It defines no independent runtime APIs. The included implementation gains CS4231-specific module description, a second DMA parameter, CS4231 fix bit programming, and WSS timer creation.

## Control Flow
Build-time control flow selects `CS4231` branches in `opti92x-ad1848.c`. Runtime probe, configuration, PnP, PM, and registration are inherited from the included file.

## State and Persistence
State is inherited from `struct snd_opti9xx` and module globals in the included implementation. The CS4231 variant adds `dma2`.

## Dependencies and Integration Points
It depends on the shared OPTi implementation and the Kbuild target `snd-opti92x-cs4231.o`.

## Risks and Test Signals
Risks are wrapper-induced symbol/metadata coupling and behavior drift from the AD1848 base. Test signals are successful CS4231 module build, second DMA validation, WSS timer availability, and correct module description.
