# sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_pwmdac.c

Purpose: StarFive JH7110 PWM-DAC ASoC DAI driver. It exposes a playback-only CPU DAI backed by a PWM-DAC FIFO register and generic dmaengine PCM.

Important APIs and types: `struct jh7110_pwmdac_dev` owns MMIO base, physical base, configuration fields, APB/core clocks, APB reset, DMA playback data, and saved CTRL register. Configuration enums represent PWM shift width, duty-cycle alignment, sample count, data-change behavior, data mode, and data shift. DAI ops cover probe, startup, hw_params, and trigger.

Control flow: probe maps the register resource, gets `apb` and `core` clocks, gets reset, initializes default PWM/DMA parameters, registers the component/DAI, registers dmaengine PCM, and enables runtime PM. `hw_params()` maps supported sample rates to `cnt_n` and core clock rates, validates mono/stereo, sets DMA bus width, programs PWM control fields, then sets the core clock rate with a small rounding margin. Trigger start/resume/pause-release reprograms and enables the PWM-DAC; stop/suspend/pause disables it. Runtime PM toggles clocks and reset deassertion. System sleep saves/restores CTRL around forced runtime suspend/resume.

State and persistence: `dev->cfg` holds desired programming, `saved_ctrl` persists CTRL over system sleep, and DMA data persists for DAI probe. The hardware CTRL register is restored on system resume, but only one register is saved.

Dependencies and integration points: device tree compatible `starfive,jh7110-pwmdac`, clock/reset framework, ASoC DAI/component APIs, generic dmaengine PCM, and DMA FIFO address at `mapbase + JH7110_PWMDAC_WDATA`.

Risks: `jh7110_pwmdac_crg_enable(false)` disables clocks but does not assert reset, so hardware state may persist differently across low-power states. `hw_params()` calls `jh7110_pwmdac_set()` before `clk_set_rate()`, so a failed clock set leaves the PWM-DAC programmed/enabled. Rate support is hand-coded; unsupported but ALSA-advertised rates in `SNDRV_PCM_RATE_8000_48000` must be checked by hw_params failures. Only CTRL is restored, not WDATA or clock rate.

Test signals: playback at 8k, 11.025k, 16k, 22.05k, 32k, 44.1k, 48k; mono versus stereo DMA widths; trigger pause/resume; runtime PM autosuspend; system suspend while configured; clock rounding validation on the target clock tree.
