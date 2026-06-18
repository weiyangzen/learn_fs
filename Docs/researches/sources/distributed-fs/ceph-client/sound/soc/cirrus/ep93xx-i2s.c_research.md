# sources/distributed-fs/ceph-client/sound/soc/cirrus/ep93xx-i2s.c

Purpose: EP93xx I2S CPU DAI driver. It manages I2S MMIO registers, mclk/sclk/lrclk clocks, FIFO enable/disable, optional IRQ watchdog recovery, DAI format and hw_params programming, and registration of the EP93xx dmaengine PCM platform.

Important APIs, types, and functions: `struct ep93xx_i2s_info` owns three clocks, MMIO base, and dmaengine DAI data. `ep93xx_i2s_enable()` and `disable()` gate clocks and TX/RX FIFOs. `ep93xx_i2s_interrupt()` resets and refills TX FIFO on underflow when the watchdog option is enabled. DAI ops include `ep93xx_i2s_dai_probe`, `startup`, `shutdown`, `set_dai_fmt`, `hw_params`, and `set_sysclk`. Component PM hooks disable/enable active streams. Probe maps registers, optionally requests IRQ, obtains clocks, registers the DAI/component, and registers PCM.

Control flow: startup enables shared clocks and global I2S if both FIFOs were previously disabled, then enables the requested FIFO and optional TX IRQs. Format setup writes RX/TX clock config and line-control registers for I2S/left/right justified, master/slave, and polarity modes. Hw_params chooses 16/24/32-bit word-length register values, computes clock divisors from MCLK and sample rate, and sets SCLK/LRCLK rates. Shutdown disables IRQs and FIFO, and if both directions are off disables global I2S and clocks.

State and persistence: runtime state is `ep93xx_i2s_info` in device drvdata plus hardware register state. Clock rates persist in clk framework state while the device is active. No storage outside runtime.

Dependencies and integration: uses ALSA SoC DAI/component APIs, dmaengine PCM support via `devm_ep93xx_pcm_platform_register()`, OF compatible `cirrus,ep9301-i2s`, platform MMIO/IRQ resources, and Cirrus EP93xx clock names `mclk`, `sclk`, `lrclk`.

Risks: DAI advertises only S32_LE via `EP93XX_I2S_FORMATS`, while hw_params has code for S16/S24/S32; that mismatch may be intentional to force 32-bit slots but should be tested. Probe uses manual `clk_get/clk_put` instead of devm clocks, so all error/remove paths must stay correct. Watchdog-enabled builds require an IRQ resource. Resume enables both playback and capture when component active, regardless of which streams were active before suspend.

Test signals: probe with and without watchdog, playback/capture at 8 kHz through 192 kHz, all supported DAI formats/polarities, sysclk changes, underflow interrupt recovery, suspend/resume with one or both directions active, and module unload to verify clocks are put.
