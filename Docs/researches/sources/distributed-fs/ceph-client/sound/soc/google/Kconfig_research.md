# sources/distributed-fs/ceph-client/sound/soc/google/Kconfig

Purpose: Kconfig menu for Google ASoC platform support. It currently exposes one tristate option, `SND_SOC_CHV3_I2S`, for the Chameleon v3 I2S device.

Important APIs/types/functions: build-time symbol `SND_SOC_CHV3_I2S`; user-facing prompt "Google Chameleon v3 I2S device".

Control flow: when selected as built-in or module, the corresponding Makefile compiles `chv3-i2s.o`.

State and persistence: no runtime state; only kernel configuration state.

Dependencies/integration: no explicit dependencies are declared here, so broader ASoC menu context must ensure sound/ASoC prerequisites. Integrates with `sound/soc/google/Makefile`.

Risks: lack of explicit dependencies can permit compile-test combinations that rely on outer menu constraints. Help text is minimal and gives no DT compatible or platform prerequisites.

Test signals: Kconfig coverage should verify `CONFIG_SND_SOC_CHV3_I2S=m/y` includes `chv3-i2s.o` and that unset excludes it.
