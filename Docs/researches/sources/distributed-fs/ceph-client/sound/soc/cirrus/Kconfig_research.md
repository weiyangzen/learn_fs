# sources/distributed-fs/ceph-client/sound/soc/cirrus/Kconfig

Purpose: Kconfig menu for Cirrus Logic EP93xx ASoC support. It gates the EP93xx platform PCM layer, the EP93xx I2S controller, and an optional watchdog workaround for transmit FIFO underflow.

Important APIs, types, and functions: declares `SND_EP93XX_SOC`, `SND_EP93XX_SOC_I2S`, and `SND_EP93XX_SOC_I2S_WATCHDOG`. `SND_EP93XX_SOC` is tristate, depends on `ARCH_EP93XX || COMPILE_TEST`, and selects `SND_SOC_GENERIC_DMAENGINE_PCM`. `SND_EP93XX_SOC_I2S` depends on the platform option. The watchdog is a bool under `if SND_EP93XX_SOC_I2S`, defaults to yes, and documents a hardware underflow workaround.

Control flow: Kconfig selection flows from platform support to I2S support to the optional watchdog. Enabling watchdog compiles IRQ-based recovery code in `ep93xx-i2s.c`.

State and persistence: build-time configuration only; no runtime state.

Dependencies and integration: integrates with the kernel sound/soc Kconfig tree and the local Cirrus Makefile. `select SND_SOC_GENERIC_DMAENGINE_PCM` matches the `ep93xx-pcm.c` use of dmaengine PCM registration.

Risks: watchdog defaults to enabled because the hardware issue is severe, so platform descriptions must provide a valid IRQ when the I2S controller is enabled. Disabling watchdog may allow byte-shifted streams after FIFO underflow.

Test signals: run Kconfig builds for `ARCH_EP93XX`, `COMPILE_TEST`, module and built-in combinations, with watchdog enabled and disabled. Confirm Makefile object selection matches the chosen symbols.
