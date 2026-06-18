# sources/distributed-fs/ceph-client/sound/soc/starfive/jh7110_tdm.c

Purpose: StarFive JH7110 TDM ASoC DAI driver with playback and capture support through one FIFO address and generic dmaengine PCM.

Important APIs and types: `struct jh7110_tdm_dev` stores MMIO base, six clocks, reset array, format polarity/sync/master settings, TX/RX channel config, sample rate/PCM clock, playback/capture DMA data, and saved registers. Enums describe master/slave, clock polarity, frame sync timing, FIFO threshold, word length, slot length, and justification. DAI ops cover probe, startup, hw_params, trigger, and set_fmt.

Control flow: probe maps MMIO, gets clock/reset resources, initializes default TDM and DMA parameters, registers component/DAI and dmaengine PCM, then enables runtime PM. `set_fmt()` accepts CPU-master (`BP_FP`) or codec-master (`BC_FC`) modes and writes global control. `hw_params()` validates 16- or 32-bit samples and 1/2/4/6/8 channels, calculates `pcmclk = channels * rate * width`, updates TX or RX slot/word/channel scaling, sets DMA width, writes stream-specific config, validates/writes sync divider, and saves context. Trigger start enables global block and stream TX/RX enable bit from saved context; stop clears the relevant stream enable bit. Runtime PM enables/disables all clocks and reset, selecting `tdm_ext` as parent for `tdm`.

State and persistence: TX and RX configurations are independent. `saved_pcmtxcr`/`saved_pcmrxcr` are stream contexts restored at trigger start; `saved_pcmgbcr` and `saved_pcmdiv` are system sleep contexts. Runtime PM does not itself save stream config.

Dependencies and integration points: compatible `starfive,jh7110-tdm`, clock names `mclk_inner`, `tdm_ahb`, `tdm_apb`, `tdm_internal`, `tdm_ext`, `tdm`, reset array, ASoC dmaengine PCM, and fixed FIFO physical address `0x170c0000`.

Risks: FIFO DMA address is hard-coded rather than derived from the mapped resource, so SoC variants or remapped resources can break. System resume writes saved registers before `pm_runtime_force_resume()`, which may access MMIO while clocks are off depending on PM state. `syncdiv` validation uses enum slot-length values, not bit counts, so confirm hardware encoding math. Full-duplex concurrent hw_params can overwrite shared `pcmclk`/divider assumptions.

Test signals: playback and capture at all advertised rates with 1/2/4/6/8 channels, 16- and 32-bit formats, master and slave format modes, full-duplex start/stop ordering, runtime/system suspend, and DMA FIFO address verification against device tree.
