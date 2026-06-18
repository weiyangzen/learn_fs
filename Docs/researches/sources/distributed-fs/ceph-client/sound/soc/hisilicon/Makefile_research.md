# sources/distributed-fs/ceph-client/sound/soc/hisilicon/Makefile

Purpose: kbuild mapping for Hisilicon ASoC platform driver objects.

Important APIs/types/functions: maps `obj-$(CONFIG_SND_I2S_HI6210_I2S)` to `hi6210-i2s.o`.

Control flow: object inclusion follows the Kconfig tristate.

State and persistence: no runtime state.

Dependencies/integration: coupled to `hisilicon/Kconfig` and `hi6210-i2s.c`.

Risks: minimal build file; future drivers need explicit object mapping.

Test signals: enabled symbol should produce the driver object; disabled symbol should omit it.
