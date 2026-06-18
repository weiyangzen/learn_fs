# sources/distributed-fs/ceph-client/sound/soc/cirrus/Makefile

Purpose: build glue for Cirrus EP93xx ASoC objects. It maps Kconfig symbols to the PCM platform object and I2S controller object.

Important APIs, types, and functions: `snd-soc-ep93xx-y := ep93xx-pcm.o` builds the PCM helper module; `snd-soc-ep93xx-i2s-y := ep93xx-i2s.o` builds the I2S controller module. `obj-$(CONFIG_SND_EP93XX_SOC)` and `obj-$(CONFIG_SND_EP93XX_SOC_I2S)` add those modules to the kernel build.

Control flow: Kbuild first expands composite object variables, then links the selected `snd-soc-ep93xx.o` and `snd-soc-ep93xx-i2s.o` depending on configuration.

State and persistence: build-time only.

Dependencies and integration: depends on the local Kconfig symbols and source filenames. The I2S object calls the exported PCM registration function from `ep93xx-pcm.c`, so module dependency/order must keep `SND_EP93XX_SOC` available when I2S is enabled.

Risks: object names must remain synchronized with Kconfig and exported symbol names. Since `SND_EP93XX_SOC_I2S` depends on `SND_EP93XX_SOC`, broken dependency edits could cause unresolved `devm_ep93xx_pcm_platform_register`.

Test signals: `make sound/soc/cirrus/` for built-in and module configs, and `modpost` should show the I2S module depending on the PCM helper when modular.
