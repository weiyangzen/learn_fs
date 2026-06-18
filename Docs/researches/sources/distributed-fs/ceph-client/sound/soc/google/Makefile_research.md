# sources/distributed-fs/ceph-client/sound/soc/google/Makefile

Purpose: build glue for Google ASoC platform drivers.

Important APIs/types/functions: maps `obj-$(CONFIG_SND_SOC_CHV3_I2S)` to `chv3-i2s.o`.

Control flow: kbuild includes `chv3-i2s.c` only when the Kconfig symbol is enabled.

State and persistence: no runtime state.

Dependencies/integration: coupled to `google/Kconfig` and the source object name.

Risks: object list has no aggregate library; additional Google drivers must be appended carefully.

Test signals: inspect built objects for enabled/disabled `CONFIG_SND_SOC_CHV3_I2S`.
