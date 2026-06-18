# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-pcm.h

Purpose: local Cirrus EP93xx PCM header exposing the dmaengine PCM registration helper.

Important APIs, types, and functions: declares `int devm_ep93xx_pcm_platform_register(struct device *dev);` with an include guard.

Control flow: none; compile-time declaration only.

State and persistence: none.

Dependencies and integration: included by `ep93xx-pcm.c` and `ep93xx-i2s.c`. It relies on callers having `struct device` visible through included kernel headers.

Risks: if included without a prior `struct device` declaration, future cleanup could require an explicit forward declaration. Otherwise the header is intentionally minimal.

Test signals: compile `ep93xx-i2s.c` and `ep93xx-pcm.c` together and as modules to verify exported symbol and prototype consistency.
