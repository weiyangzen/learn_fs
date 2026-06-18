# sources/distributed-fs/ceph-client/sound/soc/sti/sti_uniperif.c

Purpose: common STi uniperipheral platform/DAI glue. It maps device-tree compatibles to player/reader capabilities, allocates a `struct uniperif`, initializes the proper direction-specific implementation, registers one ASoC DAI, and registers generic dmaengine PCM.

Important APIs and types: `struct sti_uniperiph_dev_data` describes instance ID, IP version, stream direction, DAI name, and type. Exported common helpers include `sti_uniperiph_reset()`, `sti_uniperiph_set_tdm_slot()`, `sti_uniperiph_fix_tdm_chan()`, `sti_uniperiph_fix_tdm_format()`, `sti_uniperiph_get_tdm_word_pos()`, `sti_uniperiph_dai_probe()`, `sti_uniperiph_dai_set_fmt()`, and `sti_uniperiph_dai_hw_params()`.

Control flow: probe allocates private data and one DAI descriptor, then `sti_uniperiph_cpu_dai_of()` matches DT data, maps MMIO, calculates FIFO physical address, gets IRQ, chooses TDM or PCM mode based on `st,tdm-mode`, calls `uni_player_init()` or `uni_reader_init()`, and fills stream capabilities from `uni->hw`. DAI probe sets playback or capture DMA data to the FIFO address and 32-bit bus width, then creates controls. Common hw_params adjusts DMA maxburst based on user frame size for TDM or channel count for PCM.

State and persistence: `struct uniperif` stores type, version, MMIO, IRQ, clock/control fields, state, substream, IEC958 settings, controls, DAI format, and TDM slot settings. Suspend requires the uniperipheral to be stopped and switches pinctrl sleep/default states.

Dependencies and integration points: DT compatibles for STi players/readers, `uniperif.h` register macros, direction-specific init in `uniperif_player.c`/`uniperif_reader.c`, ASoC DAI/component APIs, pinctrl PM, dmaengine PCM, and optional syscon setup in player init.

Risks: TDM frame-size validation uses a bitmask-style allowed set on byte sizes; verify intended acceptance of 8/16/24/32 bytes. `sti_uniperiph_get_tdm_word_pos()` has no explicit failure when more slots are requested than `WORD_MAX` can represent. Suspend returns busy unless state is stopped, so system suspend can fail during active playback/capture. The code accepts multiple controls with the same name by indexing them to instance ID.

Test signals: bind every compatible, TDM and non-TDM DT modes, set TDM slots for legal and illegal frame sizes, exercise suspend while stopped and while streaming, verify DMA maxburst for PCM/TDM, and inspect ALSA controls per instance.
