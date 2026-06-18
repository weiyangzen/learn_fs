# subset-b-006391 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos_scb_lib.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos_scb_lib.c

Purpose: implements the CS46xx DSP SPOS stream-control-block (SCB) construction library. It creates, links, unlinks, and destroys DSP task SCBs for timing, codec I/O, PCM playback/capture, mixers, sample-rate conversion, asynchronous S/PDIF paths, and procfs diagnostics.

Important APIs and types: public constructors include `cs46xx_dsp_create_timing_master_scb`, `cs46xx_dsp_create_codec_out_scb`, `cs46xx_dsp_create_codec_in_scb`, `cs46xx_dsp_create_src_task_scb`, `cs46xx_dsp_create_mix_only_scb`, `cs46xx_dsp_create_mix_to_ostream_scb`, `cs46xx_dsp_create_vari_decimate_scb`, `cs46xx_dsp_create_asynch_fg_rx_scb`, `cs46xx_dsp_create_spio_write_scb`, and `cs46xx_dsp_create_magic_snoop_scb`. PCM lifecycle APIs are `cs46xx_dsp_create_pcm_channel`, `cs46xx_dsp_pcm_channel_set_period`, `cs46xx_dsp_pcm_ostream_set_period`, `cs46xx_dsp_pcm_link`, `cs46xx_dsp_pcm_unlink`, and `cs46xx_dsp_destroy_pcm_channel`. S/PDIF control is exposed through `cs46xx_dsp_enable_spdif_out`, `cs46xx_dsp_disable_spdif_out`, `cs46xx_iec958_pre_open`, and `cs46xx_iec958_post_close`.

Control flow: `_dsp_create_generic_scb` initializes raw SCB data, patches task-entry and null-list pointers, calls `cs46xx_dsp_create_scb`, links the SCB into either a parent's `sub_list_ptr` or `next_scb_ptr`, updates DSP RAM with `cs46xx_dsp_spos_update_scb`, and registers optional procfs state. `_dsp_unlink_scb` reverses parent/child list wiring and writes both affected SCBs back to DSP memory. PCM creation first chooses a mixer target, reuses an existing SRC SCB for matching sample rate and mixer when possible, otherwise allocates one of `DSP_MAX_SRC_NR` SRC slots, then allocates a PCM reader SCB in one of `DSP_MAX_PCM_CHANNELS` virtual channels.

State and persistence: mutable state lives in `struct dsp_spos_instance`: SCB descriptors, symbol table deletion markers, fragment indexes, PCM channel descriptors, SRC slot bitmap, volume defaults, S/PDIF status bits, and cached task symbols (`NULLALGORITHM`, `S16_UPSRC`). PM builds free `scb->data` on removal. Hardware-visible state is persisted by writes to DSP parameter/sample memory and by `snd_cs46xx_poke` period updates.

Dependencies and integration: depends on `cs46xx.h`, `cs46xx_lib.h`, `dsp_spos.h`, DSP symbol lookup, ALSA procfs, `snd_cs46xx_peek/poke`, and hardware helper `cs46xx_dsp_enable_spdif_hw`. It is consumed by the CS46xx ALSA PCM/mixer/SPDIF setup code and assumes the firmware symbols named in this file exist.

Risks and test signals: list mutation is guarded only around critical DSP updates, so parent/child invariants and refcounts are the main safety surface. Error paths after partially creating PCM/SRC/S/PDIF SCBs can leak until callers clean up. Period setters accept only hardware-supported powers-of-two modulo sizes from 32 to 2048. Good tests are PCM open/prepare/link/unlink/close at shared and distinct rates, SRC slot exhaustion, S/PDIF open while output monitor is enabled, procfs reads under concurrent teardown, and suspend/resume with allocated SCBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs46xx/dsp_spos_scb_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5530.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs5530.c

Purpose: ALSA PCI probe driver for Cyrix/NatSemi CS5530 VSA1 XpressAudio, presenting the hardware through the SoundBlaster 16 compatibility layer.

Important APIs and types: `struct snd_cs5530` stores ALSA card, PCI device, SB core, and PCI base. `snd_cs5530_create` enables PCI, maps BAR0, decodes softaudio configuration, reads SB mixer registers for IRQ/DMA, and creates SB DSP, PCM, and mixer devices. `snd_cs5530_probe` creates/registers the ALSA card. `snd_cs5530_mixer_read` performs the legacy indexed mixer register read.

Control flow: module parameters select ALSA card index/id/enable. Probe rejects disabled or excess card slots, allocates `snd_devm_card_new`, calls `snd_cs5530_create`, fills card strings, registers the card, and stores driver data. Creation reads config word at BAR0+0x18, derives SB base from low bits, validates enable bits, maps DMA/IRQ bitfields, and delegates most audio behavior to `snd_sbdsp_create`, `snd_sb16dsp_pcm`, and `snd_sbmixer_new`.

State and persistence: state is entirely device/runtime state; no persistent storage. PCI mapping is pcim-managed and card lifetime is devm-managed. The static `dev` cursor assigns module parameter arrays to discovered cards.

Dependencies and integration: integrates with Linux PCI core and ALSA SoundBlaster helper layer (`sound/sb.h`). It depends on firmware/BIOS VSA1 exposing correct SB emulation registers.

Risks and test signals: risk is legacy resource decoding and hardware quirks: no full-duplex native formats, unsupported DMA/IRQ bitfields, and reliance on short `udelay` timing. Test with CS5530/MediaGX hardware or emulation: module load, detected base/IRQ/DMA logging, playback, capture, mixer controls, disabled module slot handling, and failure when VSA audio is not enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/Makefile

Purpose: Kbuild fragment for the CS5535/CS5536 ALSA driver.

Important APIs and types: builds `snd-cs5535audio.o` from core `cs5535audio.o` and `cs5535audio_pcm.o`, adds `cs5535audio_pm.o` under `CONFIG_PM_SLEEP`, adds `cs5535audio_olpc.o` under `CONFIG_OLPC`, and exposes the module through `obj-$(CONFIG_SND_CS5535AUDIO)`.

Control flow and integration: this file controls which optional code paths are present at compile time. The C header provides stubs for OLPC helpers when `CONFIG_OLPC` is off, and the PCI driver's `.driver.pm` field is compiled only when PM sleep support is enabled.

State, risks, and test signals: no runtime state. Risks are configuration skew: PM or OLPC code can silently disappear from builds, so test matrix should include default, `CONFIG_PM_SLEEP`, `CONFIG_OLPC`, and both together, verifying unresolved symbols do not occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.c

Purpose: core PCI/ALSA driver for the CS5535/CS5536 companion audio function. It wires PCI resources, AC97 codec access, IRQ handling, mixer creation, PCM creation, and ALSA card registration.

Important APIs and types: `snd_cs5535audio_ids` matches NS CS5535 and AMD CS5536 audio. `snd_cs5535audio_codec_read/write` implement memory-mapped AC97 command/status transactions. `snd_cs5535audio_mixer` creates the ALSA AC97 bus/mixer and applies generic plus OLPC quirks. `snd_cs5535audio_interrupt`, `process_bm0_irq`, and `process_bm1_irq` dispatch bus-master playback/capture period interrupts. `snd_cs5535audio_create` owns PCI enable, DMA mask, region request, IRQ request, and bus mastering.

Control flow: probe allocates a devm ALSA card, sets `private_free`, creates hardware resources, initializes AC97 mixer, creates PCM via `snd_cs5535audio_pcm`, names/registers the card, and stores drvdata. Codec read/write submit commands to `ACC_CODEC_CNTL`, wait for `CMD_NEW` to clear, and for reads poll `ACC_CODEC_STATUS` until `STS_NEW` matches the requested register.

State and persistence: `struct cs5535audio` stores card, AC97, PCM, IRQ, PCI, I/O port, register spinlock, substream pointers, and playback/capture DMA state. Hardware state is in BAR0 registers; AC97 mixer state is managed by ALSA. No on-disk persistence.

Dependencies and integration: depends on Linux PCI, IRQ, I/O port access, ALSA core/control/PCM/AC97, and `cs5535audio_pcm.c`. Optional `cs5535audio_olpc.c` extends AC97 capabilities and controls.

Risks and test signals: timeout-only AC97 transactions can leave stale values; `process_bm0_irq` assumes `playback_substream` is valid when EOP arrives; unexpected BM1 IRQs are silently ignored if not EOP. Tests: probe/remove, AC97 read/write timeout behavior, playback/capture period interrupts, shared IRQ returning `IRQ_NONE` when status is zero, and card registration with both supported PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.h -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.h

Purpose: shared register map, bit definitions, data structures, and cross-file declarations for the CS5535/CS5536 audio driver.

Important APIs and types: I/O helpers `cs_writel`, `cs_writeb`, `cs_readl`, `cs_readw`, and `cs_readb` add register offsets to `cs5535audio.port`. Register constants cover AC97 codec control/status, IRQ status, bus-master command/status/PRD/pointer registers, AC97 command bits, and PRD control bits. `struct cs5535audio_dma_ops` abstracts playback versus capture register operations; `struct cs5535audio_dma_desc` describes PRD entries; `struct cs5535audio_dma` holds per-direction DMA state; `struct cs5535audio` is the driver-private card state.

Control flow and integration: the header lets `cs5535audio_pcm.c` use a common DMA operation table while `cs5535audio.c` owns device creation and IRQs. `CONFIG_OLPC` switches between real OLPC helper declarations and no-op inline stubs, allowing the same PCM/core code to call OLPC hooks unconditionally.

State and persistence: declares in-memory runtime state only: saved PRD on suspend, DMA buffer metadata, PCM open flags, and substream pointers. Hardware state is volatile register state.

Risks and test signals: register offsets and bit definitions are a single point of correctness. PRD addresses are 32-bit, matching the core driver's DMA mask. Compile-test with and without `CONFIG_OLPC` and `CONFIG_PM_SLEEP`; runtime-test playback/capture register access and PM resume PRD restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_olpc.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_olpc.c

Purpose: OLPC XO-1 board-specific extensions for CS5535 audio, handling analog input selection, microphone bias, and mixer control replacement around the AD1888 AC97 codec.

Important APIs and types: `olpc_analog_input` toggles AC97 high-pass-filter disable and `OLPC_GPIO_MIC_AC`; `olpc_mic_bias` manipulates AC97 `V_REFOUT` as mic bias. ALSA controls are `DC Mode Enable` and `MIC Bias Enable`. `olpc_prequirks` adjusts AC97 scaps for inverted EAPD on later boards; `olpc_quirks` requests/configures GPIO, removes generic controls, adds OLPC controls, and defaults mic bias off; `olpc_quirks_cleanup` frees GPIO.

Control flow: all entry points first check `machine_is_olpc` except cleanup. The core mixer path calls `olpc_prequirks` before AC97 mixer creation and `olpc_quirks` afterward. PCM capture open/close helpers in the header call `olpc_analog_input` and `olpc_mic_bias` to manage recording hardware state.

State and persistence: state is stored in GPIO output level and AC97 register bits. No persistent data; cleanup releases the GPIO line.

Dependencies and integration: depends on ALSA controls/info, AC97 AD-specific register fields, Linux GPIO API, and `asm/olpc.h`. It integrates only when `CONFIG_OLPC` is set.

Risks and test signals: `put` callbacks always return changed even if the requested state equals current state; GPIO request failure aborts mixer setup on OLPC machines. Test on OLPC and non-OLPC boot paths, control add/remove behavior, capture open/close LED/mic-bias side effects, and GPIO cleanup during card free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_olpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pcm.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pcm.c

Purpose: PCM playback/capture implementation for CS5535/CS5536 audio, including ALSA hardware capabilities, DMA PRD ring construction, trigger handling, pointer reporting, and PCM device creation.

Important APIs and types: `snd_cs5535audio_playback` and `snd_cs5535audio_capture` define S16_LE stereo continuous-rate hardware constraints. `cs5535audio_build_dma_packets` allocates and fills PRD descriptors plus a trailing jump descriptor. `snd_cs5535audio_hw_params/free`, `snd_cs5535audio_trigger`, `snd_cs5535audio_pcm_pointer`, prepare/open/close callbacks, and `snd_cs5535audio_pcm` form the ALSA PCM surface. Direction-specific `cs5535audio_dma_ops` map to BM0 playback and BM1 capture registers.

Control flow: open selects direction hardware, clamps rates from AC97 capability masks, records the substream, and assigns runtime private DMA state. `hw_params` records buffer metadata and builds descriptors. `prepare` programs AC97 DAC/ADC sample rate. `trigger` enables, pauses, resumes, or disables the correct bus-master engine under `reg_lock`. `pointer` reads the hardware DMA pointer, bounds-checks it against runtime DMA buffer, and converts bytes to frames. `hw_free` powers down the relevant AC97 path and frees descriptor pages.

State and persistence: per-direction DMA state tracks descriptor buffer, active substream, buffer address/size, period size/count, saved PRD, and open flag. Descriptor memory is allocated with ALSA DMA APIs and freed on `hw_free`.

Dependencies and integration: used by core probe after AC97 mixer creation, relies on `struct cs5535audio` and register macros from the header, and calls OLPC capture hooks unconditionally via stubs or real implementations.

Risks and test signals: descriptor allocation reserves `CS5535AUDIO_DESC_LIST_SIZE+1`, which is byte-based but intended to include an extra descriptor; period count is capped at 128. Pointer errors reset to zero and log. Tests: mmap playback/capture, period interrupts, pause/resume, all accepted period sizes/counts, `hw_params` reuse with unchanged period geometry, and capture OLPC hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pm.c -->
# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pm.c

Purpose: sleep power-management support for CS5535/CS5536 audio.

Important APIs and types: `snd_cs5535audio_stop_hardware` asserts AC-link shutdown. `snd_cs5535audio_suspend` changes ALSA power state, suspends AC97, saves active DMA PRD registers, and shuts down the link. `snd_cs5535audio_resume` warm-resets the AC link, waits for `PRM_RDY_STS`, re-prepares active substreams, restores PRD registers, resumes AC97, and returns ALSA power state to D0. `SIMPLE_DEV_PM_OPS` exports `snd_cs5535audio_pm`.

Control flow: suspend iterates both playback/capture DMA slots and saves PRD only when `substream` is non-null. Resume writes `ACC_CODEC_CNTL_LNK_WRM_RST`, polls codec status for up to 50 micro-delay iterations, then calls each active substream's `prepare` callback before restoring the saved PRD address.

State and persistence: only volatile resume state is `cs5535audio_dma.saved_prd`; codec state is delegated to AC97 suspend/resume.

Dependencies and integration: compiled under `CONFIG_PM_SLEEP` and referenced by the PCI driver's `.pm` pointer. Depends on ALSA power and AC97 PM helpers.

Risks and test signals: resume logs but continues after AC-link-ready timeout; active streams are prepared but not restarted, leaving trigger to ALSA. Test suspend/resume with idle, playback-only, capture-only, and duplex streams; verify PRD registers and AC97 rates are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/cs5535audio/cs5535audio_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/Makefile

Purpose: Kbuild fragment for the Creative X-Fi ctxfi ALSA module.

Important APIs and types: declares `snd-ctxfi-y` object composition: PCI front end `xfi.o`, ATC orchestration, VM, PCM, mixer, resource managers, SRC, AMIXER, DAIO, input mapper, hardware abstraction, timer, and chip-specific 20k1/20k2 backends. Exposes the module through `obj-$(CONFIG_SND_CTXFI)`.

Control flow and integration: build order groups the entire ctxfi subsystem into one module, so internal symbols are linked together rather than exported between modules.

State, risks, and test signals: no runtime state. Build-test should ensure both 20k1 and 20k2 hardware backends remain included when `CONFIG_SND_CTXFI` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k1reg.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k1reg.h

Purpose: register-address map for the Creative 20K1 X-Fi hardware backend.

Important APIs and types: defines DSP RAM/register ranges, transport registers, audio ring and mapper ranges, mixer operator registers, SRC/SRC manager registers, filter ranges, DAIO registers (`DAOIMAP`, `SPOS`, `SRTSCTL`, `I2SCTL`, `SPICTL`, `SPOCTL`), timer/global interrupt registers (`WC`, `TIMR`, `GIP`, `GIE`), GPIO, PLL, and global control registers.

Control flow and integration: consumed primarily by `cthw20k1.c` for indirect register access through `hw_read_20kx` and `hw_write_20kx`. Higher-level resource managers never include this map directly; they call function pointers in `struct hw`.

State and persistence: constants only; no state.

Risks and test signals: register typos directly misprogram hardware. Notable risk: large dense macro set is hard to validate without hardware. Test signal is successful 20K1 card init, SRC enable, I2S/S/PDIF routing, timer interrupts, and stable playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k1reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k2reg.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k2reg.h

Purpose: register-address map for the Creative 20K2 X-Fi hardware backend.

Important APIs and types: defines 20K2 timer, I2C, global control, PLL, SRC, GPIO, virtual memory, transport, audio I/O, and mixer register offsets. The names match the common `struct hw` operation concepts used by ctxfi resource managers.

Control flow and integration: included by the 20K2 backend, not by generic ATC or resource-manager code. It supports chip-specific implementation of the same operation table shape as 20K1.

State and persistence: constants only.

Risks and test signals: as with 20K1, wrong offsets manifest as failed card init or broken routing. Test with 20K2 models across playback, capture, S/PDIF, timer, and suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ct20k2reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.c

Purpose: resource manager and programming wrapper for X-Fi audio mixer (`AMIXER`) and summation (`SUM`) resources.

Important APIs and types: `amixer_mgr_create/destroy` and `sum_mgr_create/destroy` construct resource managers. `get_amixer_rsc`/`put_amixer_rsc` and `get_sum_rsc`/`put_sum_rsc` allocate/free hardware resource indexes. `amixer_ops` supports `set_input`, `set_scale`, `set_invalid_squash`, `set_sum`, `commit_write`, `commit_raw_write`, `setup`, and `get_scale`.

Control flow: allocation reserves one resource per master-sample-rate conjugate under `mgr_lock`, initializes a `struct rsc`, assigns operations, and writes a muted/null setup. `amixer_commit_write` iterates all conjugates, updates X input slot and SUM address for each, marks hardware fields dirty, commits through `hw->amixer_commit_write`, then restores master positions. `SUM` exposes output slots used as AMIXER accumulation targets.

State and persistence: runtime state is allocated `struct amixer`/`struct sum`, their index arrays, input/sum pointers, and hardware control blocks owned by `rsc_init`. Hardware state is rewritten on setup/uninit; no persistent storage.

Dependencies and integration: depends on `ctresource` for generic resource allocation and `cthardware` for register-programming callbacks. Used by `ctatc.c` and mixer code to route PCM/capture/Digital I/O streams.

Risks and test signals: error unwind uses loop index after partial allocation; conjugate iteration assumes `msr` does not exceed fixed `idx[8]`. Test resource exhaustion, allocation/free under concurrent mixer changes, mono SUM capture, multichannel playback routing, and get/set scale mixer controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.h

Purpose: public resource-manager interface for ctxfi AMIXER and SUM resources.

Important APIs and types: `struct sum`, `struct sum_desc`, `struct sum_mgr`, `struct amixer`, `struct amixer_rsc_ops`, `struct amixer_desc`, and `struct amixer_mgr`. Constructors/destructors are `sum_mgr_create/destroy` and `amixer_mgr_create/destroy`.

Control flow and integration: `ctatc.c` asks managers for AMIXERs/SUMs while building PCM and capture graphs; mixer code uses AMIXER ops to route and scale sources.

State and persistence: structures describe transient hardware resources and hold pointers to related `rsc`, input, and SUM objects. No standalone persistence.

Risks and test signals: fixed `idx[8]` arrays imply `msr <= 8`; callers must put resources exactly once. Compile-test consumers and runtime-test graph creation/destruction for all channel counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctamixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.c

Purpose: central Audio Transport Controller (ATC) orchestration layer for ctxfi. It identifies the card, initializes chip-specific hardware, creates resource managers, builds the internal audio topology, services PCM prepare/start/stop/position, controls input/output routing, handles S/PDIF passthrough, and supports PM resume.

Important APIs and types: exported entry points are `ct_atc_create` and `ct_atc_create_alsa_devs`. Major internal APIs include `atc_pcm_playback_prepare/start/position`, `atc_pcm_capture_prepare/start/position`, `spdif_passthru_playback_prepare`, routing controls (`select_line_in`, `select_mic_in`, `line_*_unmute`, `spdif_*`), `atc_get_resources`, `atc_connect_resources`, and `atc_release_resources`.

Control flow: creation copies `atc_preset`, identifies model via PCI quirks, creates VM, hardware object, resource managers, mixer, persistent DAIO/SRC/SRCIMP/SUM resources, connects DAIs/DAOs to mixer ports, creates timer, and registers a low-level ALSA device for cleanup. Playback prepare releases old stream resources, allocates MEMRD SRC plus AMIXERs, maps the DMA buffer into device VM, and connects SRC outputs to PCM SUMs. Capture prepare may allocate SRC conversion stages, SRCIMPs, AMIXERs, and a mono SUM, then connects mixer outputs to a MEMWR SRC. Starts program SRC addresses/states and synchronously enable SRCs.

State and persistence: `struct ct_atc` stores hardware, VM, mixer, resource managers, DAIO table, persistent SRC/SRCIMP inputs, PCM SUMs, timer, PLL rate, model/capabilities, and stream resources in `struct ct_atc_pcm`. Runtime state is hardware graph allocation plus device virtual memory mappings. PM suspend releases resources and stops hardware; resume reinitializes hardware and rebuilds topology.

Dependencies and integration: integrates `ctpcm`, `ctmixer`, `ctsrc`, `ctamixer`, `ctdaio`, `cttimer`, `ctvmem`, and chip-specific `struct hw` callbacks. ALSA PCM/mixer front ends call into this operation table.

Risks and test signals: graph construction has many partial-allocation paths; `atc_release_resources` is the critical cleanup backstop. Rate conversion logic depends on pitch thresholds and limited ROM selections. S/PDIF passthrough temporarily reinitializes SPDIF DAO and PLL. Tests should cover card model detection, all ALSA device creation, playback/capture at 32/44.1/48/96/192 kHz where supported, mono and multichannel capture, S/PDIF passthrough toggle, output switches, resource exhaustion, and suspend/resume graph rebuild.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.h

Purpose: public ATC object model and callback interface for the ctxfi subsystem.

Important APIs and types: declares ALSA logical devices `FRONT`, `SURROUND`, `CLFE`, `SIDE`, `IEC958`, `MIXER`; card identification structs; `struct ct_atc_pcm` stream-resource bundle; and `struct ct_atc`, the central operation table and state holder. Public functions are `ct_atc_create` and `ct_atc_create_alsa_devs`.

Control flow and integration: `xfi` probe creates an ATC, then PCM and mixer layers use the callback table for stream prepare/start/stop/position, route selection, mute, S/PDIF status, and capabilities. PM builds store `struct snd_pcm *pcms` for resume interaction.

State and persistence: header defines all major runtime state: resource manager array, mixer, hardware object, VM, DAIO/PCM/SRC/SRCIMP persistent resources, stream resources, PLL rate, model name, and RCA state.

Risks and test signals: broad function-pointer API means initialization must fully populate `atc_preset`; missing callbacks fail later and indirectly. Test construction, all callback invocations used by PCM/mixer controls, and PM compile/runtime paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctatc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.c

Purpose: Digital Audio I/O resource manager for ctxfi, handling DAO outputs, DAI inputs, device index translation, DAIO enable/disable, and audio input mapper programming.

Important APIs and types: `daio_mgr_create/destroy`, `get_daio_rsc`, `put_daio_rsc`, `dao_rsc_init/uninit/reinit`, `dai_rsc_init/uninit`, DAO ops (`set_spos`, `commit_write`, `set_left_input`, `set_right_input`, clear inputs), and DAI ops (`set_srt_srcl/srcr`, `set_srt_msr`, enable SRC/SRT, commit). Static maps `idx_20k1` and `idx_20k2` provide left/right resource indexes per `DAIOTYP`.

Control flow: a DAIO allocation first reserves the unique type bit, then allocates either `struct dao` for outputs or `struct dai` for inputs. DAO init disables the target output, initializes DAO config including passthrough/MSR, re-enables it, and allocates mapper pointer slots. DAI init configures sample-rate tracker control. DAO input setters allocate imapper entries for each conjugate, clear prior mappings, map input output slots to DAO left/right users, and add entries to the manager list.

State and persistence: `struct daio_mgr` stores a bitset resource allocator, locks, imapper list, and default init imap entry. DAO objects own imapper arrays and control blocks. Hardware mapping state is committed through `hw->daio_mgr_*` callbacks.

Dependencies and integration: depends on `ctresource`, `ctimap`, and `cthardware`; `ctatc.c` uses it to allocate all physical line, S/PDIF, mic, and RCA endpoints and to connect mixer output ports.

Risks and test signals: each DAIO type is single-tenant; requesting an already-used type returns `-ENOENT`. Mapper deletion restores an initial zero mapping when list becomes empty. Tests: allocate/free every supported type on 20K1 and 20K2, invalid type rejection, DAO left/right remap replacement, S/PDIF passthrough reinit, and imapper list empty restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.h

Purpose: public Digital Audio I/O resource interface for ctxfi.

Important APIs and types: `enum DAIOTYP` enumerates line outputs, S/PDIF out/in, line input, dedicated mic, RCA, and bay S/PDIF. `struct daio`, `struct dao`, `struct dai`, descriptors `dao_desc`/`daio_desc`, operation tables `dao_rsc_ops`/`dai_rsc_ops`, and `struct daio_mgr` define DAIO allocation, enable/disable, mapper management, and commits.

Control flow and integration: ATC creates the manager, requests persistent endpoint resources, then DAO/DAI ops connect those endpoints to mixer/SRC resources. The manager bridges high-level resource graphs to hardware DAIO control blocks.

State and persistence: describes transient runtime resources, imapper list state, and per-endpoint control blocks. No independent persistence.

Risks and test signals: `type`, `msr`, `passthru`, and `output` are bitfields; callers must initialize descriptors carefully. Test compile-time consumers and runtime allocation paths for all enum values valid on each chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/ctdaio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.c

Purpose: chip-neutral factory and bitfield helper implementation for ctxfi hardware objects.

Important APIs and types: `create_hw_obj` selects `create_20k1_hw_obj` or `create_20k2_hw_obj`, stores PCI/chip/model fields, and returns a `struct hw`. `destroy_hw_obj` dispatches by PCI device ID to the matching destructor. `get_field` and `set_field` extract/insert values into masked bitfields.

Control flow: ATC calls `create_hw_obj` during hardware initialization and later destroys it during cleanup. Resource managers and chip backends use `get_field/set_field` to manipulate register fields without open-coding shifts.

State and persistence: factory sets runtime object fields only. No persistent state.

Dependencies and integration: depends on `cthardware.h`, `cthw20k1.h`, `cthw20k2.h`, and Linux `WARN_ON`.

Risks and test signals: `destroy_hw_obj` switches on `hw->pci->device` while creation switches on `chip_type`; mismatch would leak or fail teardown. `get_field/set_field` warn and no-op on zero masks. Test both chip families, unknown chip failure, and bitfield helpers for low and high mask positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.h

Purpose: central hardware-abstraction contract for ctxfi chip backends.

Important APIs and types: enums `CHIPTYP`, `CTCARDS`, and `ADCSRC`; `struct card_conf`; `struct capabilities`; and `struct hw`, a large function-pointer table for card lifecycle, PLL, ADC selection, optional PM, SRC/SRCIMP/AMIXER/DAIO register programming, timer interrupts, and hardware metadata. Also declares `create_hw_obj`, `destroy_hw_obj`, `get_field`, `set_field`, and IRQ bit masks.

Control flow and integration: generic resource managers program hardware only through `struct hw` callbacks, letting 20K1 and 20K2 backends share ATC/resource-manager logic while differing in register layout.

State and persistence: `struct hw` stores PCI/card pointers, IRQ, I/O/memory bases, chip type, model, and optional IRQ callback data. Hardware register state is volatile and backend-owned.

Risks and test signals: broad callback surface makes backend completeness critical. Tests should instantiate both backends, create every resource manager, exercise SRC/AMIXER/DAIO commits, timer callback, ADC source switches, and PM callbacks where configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthardware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.c -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.c

Purpose: Creative 20K1 chip-specific implementation of the ctxfi `struct hw` abstraction. It translates generic SRC, SRCIMP, AMIXER, DAI/DAO, timer, PLL, GPIO, I2C, transport, interrupt, and card lifecycle operations into 20K1 register writes.

Important APIs and types: `struct hw20k1` embeds `struct hw` and register locks. Control-block types mirror hardware state for SRC, SRC manager, SRCIMP manager, AMIXER, DAI, DAO, and DAIO manager. Public factory/destructor are `create_20k1_hw_obj` and `destroy_20k1_hw_obj`; `ct20k1_preset` fills the operation table.

Control flow: setters update software control blocks and dirty bits. Commit functions write only dirty fields to indirect 20K1 registers. `hw_card_init` enables PCI, handles UAA-to-X-Fi switch for CTUAA, requests regions/IRQ, initializes PLL and auto-init, enables audio ring/global control, clears interrupts, configures GPIO by model, initializes transport VM page table, DAIO, DAC, ADC, and SRC audio-ring input. Interrupt handler reads `GIP`, invokes `hw->irq_callback`, acknowledges status.

State and persistence: runtime state includes I/O base, IRQ, model-specific GPIO/I2C programming, dirty control blocks, and spinlocks for indirect 20K1 and PCI register windows. PM suspend stops transport/PLL and may switch CTUAA config space; resume reruns card init.

Dependencies and integration: depends on `ct20k1reg.h`, Linux PCI/I/O/IRQ/delay, and the generic resource managers calling the `struct hw` table. DAC/ADC setup uses GPIO and PCI indirect I2C access.

Risks and test signals: busy-wait loops poll hardware without long timeout in several I2C/SRC paths; UAA mode switching rewrites PCI config space; teardown must free IRQ, unmap memory, release regions, and disable PCI exactly once. Tests: 20K1 probe/init on each model quirk, playback/capture/S/PDIF, ADC source selection, timer interrupt callback, suspend/resume, CTUAA UAA switch, and resource-manager dirty commit correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.h -->
# sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.h

Purpose: public factory header for the ctxfi 20K1 hardware backend.

Important APIs and types: declares `create_20k1_hw_obj(struct hw **rhw)` and `destroy_20k1_hw_obj(struct hw *hw)`, including `cthardware.h` for the shared `struct hw` definition.

Control flow and integration: `cthardware.c` calls these functions when `chip_type` or PCI device indicates a 20K1 card. Generic ATC code never directly uses 20K1 internals beyond this factory interface.

State and persistence: no state; exposes constructors for the backend object.

Risks and test signals: header/API mismatch with `cthw20k1.c` would break module build. Test by compiling `CONFIG_SND_CTXFI` and probing a 20K1 device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ctxfi/cthw20k1.h -->
