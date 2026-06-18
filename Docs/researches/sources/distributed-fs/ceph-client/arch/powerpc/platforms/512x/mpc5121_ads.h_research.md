# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads.h

## Purpose
`mpc5121_ads.h` is a small board-private header for MPC5121 ADS CPLD support.

## Important APIs, Types, and Functions
It declares `mpc5121_ads_cpld_map()` and `mpc5121_ads_cpld_pic_init()`, both marked `__init`, for use by the ADS machine file.

## Control Flow, State, and Persistence
The header owns no state. It enforces a narrow interface from board setup to the CPLD interrupt implementation.

## Dependencies and Integration Points
It is included by `mpc5121_ads.c` and `mpc5121_ads_cpld.c`. The calls are sequenced so register mapping happens during architecture setup and IRQ-domain setup happens during interrupt initialization.

## Risks and Test Signals
The main risk is interface drift if CPLD initialization gains dependencies not reflected in this header. Build coverage for `CONFIG_MPC5121_ADS` and boot-time CPLD IRQ tests are sufficient signals.
