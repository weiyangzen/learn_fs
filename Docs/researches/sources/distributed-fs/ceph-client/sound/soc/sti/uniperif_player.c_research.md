# sources/distributed-fs/ceph-client/sound/soc/sti/uniperif_player.c

Purpose: STi uniperipheral playback implementation for PCM, HDMI/SPDIF IEC958, and TDM player modes. It provides DAI operations and initialization consumed by common probe code.

Important APIs and types: exported `uni_player_init()` and `uni_player_resume()`; internal IRQ handler, clock adjustment, IEC958 channel-status controls, prepare functions for IEC958/PCM/TDM, start/stop/trigger/shutdown, set_sysclk, and DT audio-glue parsing. ALSA controls expose IEC958 status and playback oversampling frequency adjustment.

Control flow: init sets stopped state and DAI ops, parses syscon audio glue fields, enables underflow recovery on newer IP, chooses hardware constraints, gets the clock, selects frequency synthesizer, optionally connects I2S/TDM TX bus, requests IRQ, initializes locks, disables idle/back-stall/rounding/SPDIF latency defaults, and installs controls. Startup stores the substream and adds TDM hw rules when needed. Prepare validates stopped state, computes DMA trigger limit, dispatches to IEC958/PCM/TDM format setup, applies DAI inversion/format, resets hardware, and leaves it ready. Start enables the clock, clears/masks interrupts, resets hardware, sets PCM data operation, applies channel status update, and marks started. Stop sets operation off, resets, masks interrupts, disables clock, and marks stopped. IRQ handles underflow, DMA errors, and underflow recovery events, stopping the PCM stream on unrecovered XRUNs.

State and persistence: `player->state`, `substream`, `mclk`, `clk_adj`, `stream_settings`, `underflow_enabled`, and control locks persist while device is bound. IEC958 status is kept in memory and programmed to channel status registers during prepare/control updates. Clock adjustment mutates the requested clock rate in ppm.

Dependencies and integration points: common `sti_uniperif.c`, `uniperif.h`, syscon `st,syscfg`, regmap fields, IRQF_SHARED, ALSA controls, clock framework, and ASoC DAI callbacks.

Risks: trigger limit validation uses `!trigger_limit % 2`, which due to precedence tests `(!trigger_limit) % 2` rather than evenness; the same pattern exists in reader. The IRQ handler assigns `ret = -EPERM` to an `irqreturn_t`. Control update calls channel-status programming under both mutex and IRQ spinlock; ensure no sleeping operations are introduced there. Stop from shutdown occurs under `irq_lock` and calls functions that may touch clocks/MMIO. TDM clock setup bypasses `set_sysclk`.

Test signals: playback in PCM, HDMI, SPDIF, and TDM modes; IEC958 control updates before/during stream; underflow recovery done/failed interrupts; invalid trigger-limit cases; clock adjustment extremes; suspend/resume; shutdown while active; TDM slot constraints.
