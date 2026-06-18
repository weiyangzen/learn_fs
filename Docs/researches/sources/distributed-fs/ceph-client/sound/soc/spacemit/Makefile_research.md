# sources/distributed-fs/ceph-client/sound/soc/spacemit/Makefile

Purpose: builds the SpacemiT K1 I2S ASoC driver.

Important APIs/types: `snd-soc-k1-i2s-y := k1_i2s.o` and `obj-$(CONFIG_SND_SOC_K1_I2S) += snd-soc-k1-i2s.o`.

Control flow/state: no runtime state.

Dependencies/integration: ties the Kconfig symbol to the single driver source file.

Risks/test signals: verify module object naming matches packaging and modprobe expectations.
